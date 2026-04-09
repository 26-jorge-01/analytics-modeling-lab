import sys
import traceback
import logging
from logging import getLogger, INFO, FileHandler, StreamHandler
import re
import pandas as pd
import json
import time
import argparse
from datetime import datetime, timedelta
import threading
from queue import Queue
from sqlalchemy import text

# Configure logging
log_file = "ingestion/api_debug_internal.log"
logger = getLogger(__name__)
logger.setLevel(INFO)

if logger.hasHandlers():
    logger.handlers.clear()

fh = FileHandler(log_file, mode='w')
fh.setFormatter(logging.Formatter("%(asctime)s - %(threadName)s - %(levelname)s - %(message)s"))
logger.addHandler(fh)

sh = StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter("%(asctime)s - %(threadName)s - %(levelname)s - %(message)s"))
logger.addHandler(sh)

try:
    from load_core import get_engine, ensure_schema_exists, RAW_SCHEMA, dataframe_to_postgres
    import uuid
    from pysecop import SecopClient, QueryBuilder, DATASETS
except ImportError as e:
    logger.error(f"Failed to import dependencies: {e}")
    sys.exit(1)

def clean_cols_vectorized(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorized Postgres-safe column name cleaning with :id preservation."""
    import unicodedata
    
    def _normalize(c):
        original_c = str(c)
        # Special case: preserve Socrata internal ID
        if original_c == ":id": return "id"
        
        c = "".join(ch for ch in unicodedata.normalize('NFKD', original_c) if not unicodedata.combining(ch))
        c = c.lower().strip().replace(" ", "_").replace("-", "_").replace(".", "_")
        c = re.sub(r'[^a-z0-9_]', '', c)
        return c[:63]
    
    df.columns = [_normalize(c) for c in df.columns]
    return df

def serialize_complex_vectorized(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorized serialization for complex types."""
    obj_cols = df.select_dtypes(include=['object']).columns
    for col in obj_cols:
        # We only serialize if the column contains dicts or lists
        # Using a sample to check if serialization is needed to save time
        sample = df[col].dropna().head(1)
        if not sample.empty and isinstance(sample.iloc[0], (dict, list)):
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)
    return df

class MatrixStreamer:
    """
    High-performance orchestrator for the SECOP Unified Matrix.
    Uses a producer-consumer pattern to overlap API I/O and DB I/O.
    """
    def __init__(self, table_name="raw_secop_api_contracts"):
        self.engine = get_engine()
        self.client = SecopClient()
        self.table_name = table_name
        self.queue = Queue(maxsize=20) # Increased buffer for high-concurrency
        self.stop_event = threading.Event()
        self.total_ingested = 0
        self._worker_signals = 0 # Track active fetchers for clean shutdown
        ensure_schema_exists(self.engine, RAW_SCHEMA)

    def finalize_sync(self):
        """'Seals' the table by creating high-performance indexes AFTER bulk ingestion."""
        with self.engine.connect() as conn:
            # PERFORMANCE INDEXES (Deferred for speed)
            logger.info("MAINTENANCE: Creating performance indexes (Deferred phase)...")
            # We use CONCURRENTLY if table is huge, but here we just do standard for a fresh load
            conn.execute(text(f'CREATE INDEX IF NOT EXISTS idx_secop_watermark ON "{RAW_SCHEMA}"."{self.table_name}" (source, ultima_actualizacion)'))
            conn.execute(text(f'CREATE INDEX IF NOT EXISTS idx_secop_dedup ON "{RAW_SCHEMA}"."{self.table_name}" (source, id_contrato)'))
            conn.commit()
            logger.info("MAINTENANCE: Indexes created successfully.")

    def _get_watermarks(self, source_label):
        try:
            with self.engine.connect() as conn:
                res = conn.execute(text(f"""
                    SELECT MAX(ultima_actualizacion) FROM "{RAW_SCHEMA}"."{self.table_name}"
                    WHERE source = :s
                """), {"s": source_label}).scalar()
                return res
        except:
            return None

    def _ensure_metadata_table(self):
        """Ensures the ingestion metadata table and columns exist before any worker starts."""
        with self.engine.connect() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{RAW_SCHEMA}"."ingestion_metadata" (
                    source TEXT PRIMARY KEY,
                    historical_offset BIGINT DEFAULT 0,
                    historical_watermark TIMESTAMP,
                    last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            # Migration check: Add historical_watermark if column doesn't exist
            try:
                conn.execute(text(f'ALTER TABLE "{RAW_SCHEMA}"."ingestion_metadata" ADD COLUMN IF NOT EXISTS historical_watermark TIMESTAMP'))
            except: pass
            conn.commit()

    def _ensure_data_table(self, df: pd.DataFrame):
        """
        Creates/Refreshes the main contracts table with a DEFINITIVE 6-column Business Primary Key.
        SCHEMA GUARD: Resolves ON CONFLICT mismatches by ensuring physical PK == definite_pk.
        """
        from sqlalchemy import inspect
        definite_pk = ["id_contrato", "proceso_de_compra", "documento_proveedor", "codigo_entidad", "ultima_actualizacion", "source"]
        
        with self.engine.connect() as conn:
            # Inspection-based Schema Guard
            inspector = inspect(self.engine)
            # Normalize schema/table checking
            has_table = inspector.has_table(self.table_name, schema=RAW_SCHEMA)
            
            if has_table:
                pk_info = inspector.get_pk_constraint(self.table_name, schema=RAW_SCHEMA)
                existing_pk = pk_info.get("constrained_columns", [])
                
                # Compare sets to avoid ordering issues
                if set(existing_pk) != set(definite_pk):
                    logger.warning(f"DB: PK MISMATCH detected (Existing: {existing_pk}). DROPPING table to enforce 6-column Business PK...")
                    conn.execute(text(f'DROP TABLE IF EXISTS "{RAW_SCHEMA}"."{self.table_name}" CASCADE'))
                    conn.commit()
                    has_table = False

            if not has_table:
                cols = df.columns.tolist()
                logger.info(f"DB: Creating data table with DEFINITIVE Business Key: {definite_pk}")
                
                col_definitions = []
                for col in cols:
                    # Type mapping
                    if col == "ultima_actualizacion":
                        col_type = "TIMESTAMP"
                    elif "valor" in col.lower() or "precio" in col.lower():
                        col_type = "NUMERIC"
                    else:
                        col_type = "TEXT"
                    
                    # DEFINITIVE PK columns must be NOT NULL
                    null_constraint = "NOT NULL" if col in definite_pk else ""
                    col_definitions.append(f'"{col}" {col_type} {null_constraint}')
                
                pk_cols_str = ", ".join([f'"{c}"' for c in definite_pk])
                pk_clause = f"PRIMARY KEY ({pk_cols_str})"
                
                conn.execute(text(f"""
                    CREATE TABLE "{RAW_SCHEMA}"."{self.table_name}" (
                        {", ".join(col_definitions)},
                        {pk_clause}
                    )
                """))
                conn.commit()
            else:
                logger.info("DB: Dynamic table check: Primary Key is valid.")

    def _get_metadata(self, source_key):
        with self.engine.connect() as conn:
            row = conn.execute(text(f'SELECT historical_offset, historical_watermark FROM "{RAW_SCHEMA}"."ingestion_metadata" WHERE source = :s'), {"s": source_key}).fetchone()
            if row:
                return row[0], row[1]
            return 0, None

    def _update_metadata(self, source_key, offset, watermark):
        with self.engine.connect() as conn:
            conn.execute(text(f"""
                INSERT INTO "{RAW_SCHEMA}"."ingestion_metadata" (source, historical_offset, historical_watermark, last_run)
                VALUES (:s, :o, :w, CURRENT_TIMESTAMP)
                ON CONFLICT (source) DO UPDATE SET 
                    historical_offset = :o, 
                    historical_watermark = :w,
                    last_run = CURRENT_TIMESTAMP
            """), {"s": source_key, "o": offset, "w": watermark})
            conn.commit()

    def fetcher_worker(self, source_label, mode="frontier", limit=0):
        """Producer: Fetches data from SECOP API using Seek-based pagination."""
        logger.info(f"FETCHER ({source_label} - {mode}): Starting...")
        
        # 1. State Recovery
        # Source labels in API are 'SECOP I' and 'SECOP II', but internally we might use underscores
        api_source = source_label.replace('_', ' ')
        
        current_offset = 0
        current_watermark = None
        
        if mode == "scavenger":
            current_offset, current_watermark = self._get_metadata(source_label)
            logger.info(f"FETCHER ({source_label} - SCAVENGER): Resuming from offset {current_offset}")

        records_processed = 0
        batch_size = 2000 # High-throughput batching

        while not self.stop_event.is_set():
            try:
                if limit > 0 and records_processed >= limit:
                    logger.info(f"FETCHER ({source_label} - {mode}): Limit reached ({limit}). Stopping.")
                    break

                # 2. Fetch from API using unified search method
                df = self.client.search(
                    datasets=[api_source.replace(' ', '_')], # pysecop search expects underscores in dataset keys
                    limit=batch_size, 
                    offset=current_offset,
                    content_type="csv"
                )

                if df.empty:
                    logger.info(f"FETCHER ({source_label} - {mode}): API Exhausted.")
                    break

                # 3. Micro-Batch Pre-processing (Vectorized)
                df = clean_cols_vectorized(df)
                df = serialize_complex_vectorized(df)
                
                # 4. Prepare for Transfer
                batch_len = len(df)
                current_offset += batch_len
                records_processed += batch_len
                
                # Get the latest watermark in this batch
                if 'ultima_actualizacion' in df.columns:
                    batch_watermark = df['ultima_actualizacion'].max()
                else:
                    batch_watermark = current_watermark

                # 5. Hand-off to Consumer
                # We send (source, mode, new_offset, new_watermark, dataframe)
                self.queue.put((source_label, mode, current_offset, batch_watermark, df))
                
                logger.info(f"FETCHER ({source_label} - {mode}): Queued batch ({batch_len} rows). Total Offset: {current_offset}")

                # Rate limiting guard
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"FETCHER ERROR ({source_label}): {e}")
                time.sleep(5) # Backoff
                continue

    def writer_worker(self):
        """Consumer: Pulls from queue and writes to Postgres using COPY + Atomic Merge."""
        logger.info("WRITER: Starting high-speed ingestor...")
        while True:
            item = self.queue.get()
            if item is None:
                break
            
            source_key, mode, new_offset, new_watermark, df = item
            try:
                # PERFORMANCE & INTEGRITY: Use a Staging-Merge pattern
                definite_pk = ["id_contrato", "proceso_de_compra", "documento_proveedor", "codigo_entidad", "ultima_actualizacion", "source"]
                
                # 0. ENSURE DEFINITIVE PK COLUMNS EXIST & ARE NOT NULL
                df['source'] = source_key.replace('_', ' ')
                for col in definite_pk:
                    if col not in df.columns:
                        df[col] = None # Will be filled below
                    
                    if col == 'ultima_actualizacion':
                        df[col] = df[col].fillna(pd.Timestamp('1900-01-01'))
                    else:
                        df[col] = df[col].fillna('N/A').astype(str)

                # 1. (DEPRECATED: Now handled in run_sync pre-flight)
                # Schema Guard is now serialized.
                
                # 2. ATOMIC MERGE: Use a single transaction for Staging -> Merge -> Commit
                unique_id = uuid.uuid4().hex
                staging_table = f"staging_{unique_id}"
                
                with self.engine.begin() as conn:
                    # A. Create isolated staging table
                    conn.execute(text(f"CREATE TEMP TABLE {staging_table} AS SELECT * FROM {RAW_SCHEMA}.{self.table_name} WITH NO DATA"))
                    
                    # B. High-speed insert to staging (using SAME connection)
                    # We pass 'conn' to ensure the TEMP table is visible
                    df.to_sql(
                        name=staging_table, 
                        con=conn, 
                        if_exists='append', 
                        index=False, 
                        method='multi', 
                        chunksize=1000
                    )
                    
                    # C. Merge to Final (Idempotent Merge)
                    cols = [f'"{c}"' for c in df.columns]
                    pk_cols_str = ", ".join([f'"{c}"' for c in definite_pk])
                    insert_query = f"""
                        INSERT INTO "{RAW_SCHEMA}"."{self.table_name}" ({', '.join(cols)})
                        SELECT {', '.join(cols)} FROM {staging_table}
                        ON CONFLICT ({pk_cols_str}) DO NOTHING
                    """
                    conn.execute(text(insert_query))
                
                # Transaction committed automatically here. Staging table cleaned up.

                self.total_ingested += 1
                
                # Unified Progress Tracking
                self._update_metadata(source_key, new_offset, new_watermark)
                
                logger.info(f"WRITER: Success. Batch {self.total_ingested} committed (Atomic Merge).")
            except Exception as e:
                logger.error(f"WRITER ERROR: {e}")
                import traceback
                logger.error(traceback.format_exc())
            finally:
                self.queue.task_done()

    def sync_dataset(self, source_key, scavenger_limit):
        """Full lifecycle for a single dataset: Frontier then Scavenger."""
        # Phase 1: Frontier
        # Phase 1: Frontier (Unlimited by default to catch all recent updates)
        self.fetcher_worker(source_key, mode="frontier", limit=0)
        
        # CRITICAL REFINEMENT: Wait for the writer queue to be exhausted before switching modes.
        # This ensures the metadata table is fully updated before the Scavenger checks it.
        logger.info(f"SyncStream-{source_key}: Waiting for Frontier batches to commit...")
        self.queue.join()
        
        # Phase 2: Scavenger
        self.fetcher_worker(source_key, mode="scavenger", limit=scavenger_limit)
        self.queue.join() # Ensure scavenger also finishes before signaling worker completion
        
        with threading.Lock():
            self._worker_signals -= 1
            if self._worker_signals == 0:
                self.queue.put(None) # Final signal for writer

    def run_sync(self, scavenger_limit=100000):
        # 0. Ensure schema and metadata table exist before any thread starts
        self._ensure_metadata_table()
        
        # --- PHASE 0: SERIALIZED SCHEMA INITIALIZATION ---
        # Fetch samples from both datasets to ensure the 'Zero-Loss' Unified Schema is fully initialized
        logger.info("ORCHESTRATOR: Performing Pre-sync Schema Guard (Union Fetch)...")
        try:
            # We fetch 1 record from each dataset to define the full contract matrix schema
            sample_df = self.client.search(datasets=["SECOP_I", "SECOP_II"], limit=1, content_type="csv")
            
            if not sample_df.empty:
                sample_df = clean_cols_vectorized(sample_df)
                sample_df['source'] = 'initialization'
                self._ensure_data_table(sample_df)
                logger.info("ORCHESTRATOR: Schema Guard check passed.")
        except Exception as e:
            logger.warning(f"ORCHESTRATOR: Pre-sync sample fetch failed ({e}). Proceeding carefully...")

        # 1. Start Writer Thread
        writer = threading.Thread(target=self.writer_worker, name="WriterThread", daemon=True)
        writer.start()

        datasets = ["SECOP_I", "SECOP_II"]
        self._worker_signals = len(datasets)

        # 2. DECOUPLED PARALLEL SYNC: Dataset-at-a-time (Frontier -> Scavenger)
        logger.info(f"--- STARTING DECOUPLED SYNC CYCLE ({len(datasets)} Parallel Streams) ---")
        dataset_threads = []
        for source in datasets:
            t = threading.Thread(
                target=self.sync_dataset, 
                args=(source, scavenger_limit), 
                name=f"SyncStream-{source}"
            )
            t.start()
            dataset_threads.append(t)
        
        for t in dataset_threads:
            t.join() 
        
        # 4. Clean shutdown
        writer.join()
        
        # 5. FINALIZATION: Create Indexes
        self.finalize_sync()
        logger.info(f"Sync Cycle Complete. Total batches processed: {self.total_ingested}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SECOP High-Performance Unified Ingestor")
    parser.add_argument("--full-backfill", action="store_true")
    parser.add_argument("--scavenge-limit", type=int, default=0, help="Max records for scavenger (0 for unlimited)")
    
    # Backward compatibility arguments (ignored or aliased)
    parser.add_argument("--start-year", type=int, help="Legacy: Scavenger now handles historical depth automatically")
    parser.add_argument("--full", action="store_true", help="Alias for --full-backfill")
    
    args = parser.parse_args()

    # Alias legacy --full to modern --full-backfill
    is_full = args.full_backfill or args.full

    streamer = MatrixStreamer()
    
    if is_full:
        logger.warning("TRUNCATING archive for full backfill...")
        with streamer.engine.connect() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS "{RAW_SCHEMA}"."{streamer.table_name}" CASCADE'))
            conn.execute(text(f'DROP TABLE IF EXISTS "{RAW_SCHEMA}"."ingestion_metadata" CASCADE'))
            conn.commit()
            # We let the FIRST batch of data create the table naturally to ensure ZERO DATA LOSS

    streamer.run_sync(scavenger_limit=args.scavenge_limit)
