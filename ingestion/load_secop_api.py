import sys
import traceback
import logging
from logging import getLogger, INFO, FileHandler, StreamHandler
import re
import pandas as pd
import json
import time
import argparse
import unicodedata
from datetime import datetime, timedelta
import threading
from queue import Queue
from sqlalchemy import text
import uuid
import hashlib

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
    from pysecop import SecopClient, QueryBuilder, DATASETS
    from pysecop.utils import normalize_dataframe, get_unified_columns, get_mapped_column
except ImportError as e:
    logger.error(f"Failed to import dependencies: {e}")
    sys.exit(1)

def sanitize_db_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Postgres-safe column name sanitization."""
    def _normalize(c):
        original_c = str(c)
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
        sample = df[col].dropna().head(1)
        if not sample.empty and isinstance(sample.iloc[0], (dict, list)):
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)
    return df

class MatrixStreamer:
    def __init__(self, table_name="secop_contracts"):
        self.engine = get_engine()
        self.client = SecopClient()
        self.table_name = table_name
        self.queue = Queue(maxsize=20)
        self.stop_event = threading.Event()
        self.total_ingested = 0
        self._worker_signals = 0
        self.fatal_error = None
        ensure_schema_exists(self.engine, RAW_SCHEMA)
        self._ensure_metadata_exists()

    def _ensure_metadata_exists(self):
        """Create state tracking table if missing."""
        # Using a raw SQL approach for reliability
        with self.engine.begin() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{RAW_SCHEMA}"."ingestion_metadata" (
                    source VARCHAR(255) PRIMARY KEY,
                    historical_offset INTEGER DEFAULT 0,
                    historical_watermark TIMESTAMP,
                    last_run TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

    def _table_exists(self):
        with self.engine.connect() as conn:
            query = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = :s AND table_name = :t)")
            return conn.execute(query, {"s": RAW_SCHEMA, "t": self.table_name}).scalar()

    def _create_table(self, df=None):
        logger.info(f"Target table {RAW_SCHEMA}.{self.table_name} not found. Creating from Unified Schema...")
        
        # 1. Get Canonical Unified Schema from pysecop
        unified_cols = get_unified_columns()
        
        # 2. Add technical metadata columns
        tech_cols = ["source", "hash_id", "ingested_at"]
        all_cols = list(set(unified_cols + tech_cols))
        
        # 3. Create dummy DF for schema inference
        schema_df = pd.DataFrame(columns=all_cols)
        
        # Create table with pandas
        schema_df.to_sql(
            name=self.table_name,
            con=self.engine,
            schema=RAW_SCHEMA,
            if_exists='replace',
            index=False
        )
        
        # 4. Add primary key constraint on hash_id
        with self.engine.begin() as conn:
            conn.execute(text(f'ALTER TABLE "{RAW_SCHEMA}"."{self.table_name}" ADD PRIMARY KEY (hash_id)'))
            
        logger.info(f"Unified table {RAW_SCHEMA}.{self.table_name} created with {len(all_cols)} columns.")

    def finalize_sync(self):
        """Indexes and maintenance after bulk ingestion."""
        if self.fatal_error:
            raise self.fatal_error
            
        if not self._table_exists():
            logger.warning("MAINTENANCE: Table does not exist. Skipping index creation.")
            return

        with self.engine.connect() as conn:
            logger.info("MAINTENANCE: Creating performance indexes...")
            
            # Helper to create index only if column exists
            def safe_create_index(idx_name, columns):
                # Check if all columns exist
                for col in columns:
                    check = conn.execute(text(f"SELECT 1 FROM information_schema.columns WHERE table_schema = :s AND table_name = :t AND column_name = :c"), {"s": RAW_SCHEMA, "t": self.table_name, "c": col}).fetchone()
                    if not check:
                        logger.warning(f"Skipping index {idx_name}: column {col} missing.")
                        return
                
                cols_str = ", ".join(columns)
                conn.execute(text(f'CREATE INDEX IF NOT EXISTS {idx_name} ON "{RAW_SCHEMA}"."{self.table_name}" ({cols_str})'))

            safe_create_index("idx_secop_watermark", ["source", "ultima_actualizacion"])
            safe_create_index("idx_secop_dedup", ["source", "id_contrato"])
            safe_create_index("idx_secop_dedup_adjudicacion", ["source", "id_adjudicacion"])
            
            conn.commit()

    def _get_data_watermark(self, source_label):
        try:
            with self.engine.connect() as conn:
                res = conn.execute(text(f"""
                    SELECT MAX(ultima_actualizacion) FROM "{RAW_SCHEMA}"."{self.table_name}"
                    WHERE source = :s AND ultima_actualizacion > '1900-01-01'
                """), {"s": source_label.replace('_', ' ')}).scalar()
                return res
        except: return None

    def _get_metadata(self, source_key):
        with self.engine.connect() as conn:
            row = conn.execute(text(f'SELECT historical_offset, historical_watermark FROM "{RAW_SCHEMA}"."ingestion_metadata" WHERE source = :s'), {"s": source_key}).fetchone()
            return (row[0], row[1]) if row else (0, None)

    def _update_metadata(self, source_key, offset, watermark):
        with self.engine.connect() as conn:
            query = f"""
                INSERT INTO "{RAW_SCHEMA}"."ingestion_metadata" (source, historical_offset, historical_watermark, last_run)
                VALUES (:s, :o, :w, CURRENT_TIMESTAMP)
                ON CONFLICT (source) DO UPDATE SET 
                    historical_offset = EXCLUDED.historical_offset, 
                    historical_watermark = EXCLUDED.historical_watermark,
                    last_run = CURRENT_TIMESTAMP
            """
            conn.execute(text(query), {"s": source_key, "o": offset, "w": watermark})
            conn.commit()

    def make_hash(self, row):
        """Zero-Loss Deterministic Hashing."""
        try:
            # Identifiers + System ID for absolute uniqueness
            ident_parts = [
                str(row.get('source', '')).strip().upper(),
                str(row.get('id_contrato', '')).strip().upper(),
                str(row.get('proceso_de_compra', '')).strip().upper(),
                str(row.get('nit_entidad', '')).strip().upper(),
                str(row.get(':id', '')).strip() # Socrata internal ID
            ]
            
            # Watermark hardening (Optional but helps detect changes)
            ua = row.get('ultima_actualizacion')
            ua_str = '1900-01-01T00:00:00.000000'
            if pd.notnull(ua):
                try: ua_str = pd.to_datetime(ua).strftime('%Y-%m-%dT%H:%M:%S.%f')
                except: pass
            ident_parts.append(ua_str)
            
            identity = "|".join(ident_parts)
            
            # Content fingerprint
            exclude = {'hash_id', 'ingested_at', 'id', 'uid'}
            content_row = {str(k): str(v) for k, v in row.items() if k not in exclude}
            content_str = json.dumps(content_row, sort_keys=True)
            
            return hashlib.md5(f"{identity}||{content_str}".encode('utf-8')).hexdigest()
        except:
            # Fallback for extreme cases to avoid thread crash
            return hashlib.md5(str(row).encode('utf-8')).hexdigest()

    def fetcher_worker(self, source_label, mode="sync", limit=0, date_filter=None):
        """Unified fetcher for both incremental and sliced-backfill."""
        from pysecop import QueryBuilder
        from pysecop.utils.helpers import get_mapped_column
        
        logger.info(f"FETCHER ({source_label} - {mode}): Starting...")
        api_source = source_label.replace('_', ' ')
        search_limit = 50000 
        ua_col = get_mapped_column(source_label, "ultima_actualizacion")
        
        # Paging state recovery
        state_key = source_label if mode == "sync" else f"{source_label}:{date_filter}"
        h_offset, h_watermark = self._get_metadata(state_key)
        
        last_watermark = h_watermark
        offset_within_watermark = h_offset
        total_fetched_this_source = 0
        
        logger.info(f"FETCHER ({source_label} - {mode}): Resuming from watermark={last_watermark}, offset={offset_within_watermark}")
        
        while not self.stop_event.is_set():
            try:
                qb = QueryBuilder()
                qb.select(["*", ":id"]) # Ensure system :id is fetched for stable paging
                
                # BASE FILTERS
                if source_label == "SECOP_I":
                    qb.where_custom("upper(estado_del_proceso) = 'ADJUDICADO'")

                if mode == "backfill" and date_filter:
                    qb.where_custom(date_filter)
                    # We still use Keyset pagination within the backfill slice
                    if last_watermark:
                        # Slice further by progress
                        ts = last_watermark
                        if not isinstance(ts, str): ts = pd.to_datetime(ts).isoformat()
                        qb.where_custom(f"{ua_col} >= '{ts}'")
                elif mode == "sync":
                    current_wm = last_watermark or self._get_data_watermark(source_label)
                    if current_wm:
                        ts = current_wm
                        if not isinstance(ts, str): ts = pd.to_datetime(ts).isoformat()
                        qb.where_custom(f"{ua_col} >= '{ts}'")
                
                # Stable Paging Configuration
                # Megastream: We use :id as the primary sort to guarantee zero-loss over 5M+ records
                qb.order(":id", "ASC") 
                qb.limit(search_limit)
                qb.offset(offset_within_watermark)

                # Fetch batch
                df = self.client.fetch(source_label, qb, content_type="json")
                if df.empty: break
                
                # Robust Date Handling (fix TypeError in comparisons)
                df[ua_col] = pd.to_datetime(df[ua_col], errors='coerce')
                
                if mode == "backfill":
                    # For historical backfill, we MUST NOT lose data even if ua_col is null
                    df[ua_col] = df[ua_col].fillna(pd.Timestamp("1900-01-01"))
                else:
                    # In sync mode, only keep records with valid update dates for correct watermarking
                    df = df.dropna(subset=[ua_col])
                    
                if df.empty: break

                # Update Paging Logic for next iteration
                # In Megastream mode, we primarily move by OFFSET within a stable :id sort
                current_batch_last_wm = df[ua_col].iloc[-1]
                
                # Update offset for next batch
                offset_within_watermark += len(df)
                last_watermark = current_batch_last_wm
                
                logger.info(f"FETCHER ({source_label}): Progressed to offset {offset_within_watermark}. Batch last watermark: {last_watermark}")
                
                # Processing using pysecop official logic
                df['source'] = api_source
                df = normalize_dataframe(df, source_label)
                
                # Vectorized serialization (fixes 'can't adapt type dict')
                df = serialize_complex_vectorized(df)
                
                # Cleanup system columns that might collide with unified matrix
                for c in ['id', 'uid', ':id']:
                    if c in df.columns:
                         df.drop(columns=[c], inplace=True)
                
                # Generate unique Hash ID for upsert/deduplication
                df['hash_id'] = df.apply(self.make_hash, axis=1)
                df['ingested_at'] = datetime.now()
                
                self.queue.put((state_key, mode, offset_within_watermark, last_watermark, df))
                total_fetched_this_source += len(df)
                
                if limit > 0 and total_fetched_this_source >= limit: break
                if len(df) < search_limit: break
                time.sleep(0.1)
            except Exception as e:
                # Throttling Resilience (Exponential Backoff)
                error_msg = str(e).lower()
                if "429" in error_msg or "throttle" in error_msg:
                    wait_time = 30 # Socrata usually throttles for 30-60s
                    logger.warning(f"FETCHER ({source_label}): Throttled by Socrata. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"FETCHER ERROR ({source_label}): {e}\n{traceback.format_exc()}")
                    time.sleep(5)

    def writer_worker(self):
        """Consumer: Atomic Merge to Postgres."""
        while True:
            item = self.queue.get()
            if item is None: break
            source_key, mode, n_offset, n_watermark, df = item
            try:
                if not self._table_exists():
                    self._create_table(df)
                    
                unique_id = uuid.uuid4().hex
                staging_table = f"staging_{unique_id}"
                
                # SCHEMA ALIGNMENT:
                # Ensure the staging table exists with a schema that matches the final table
                # We do this by selecting from the final table with a false condition
                with self.engine.begin() as conn:
                    # Resolve differences between SECOP I and II on-the-fly
                    # If target table exists, aligned df to it
                    # SCHEMA EVOLUTION:
                    # Add missing columns to the target table before attempting to use it for LIKE
                    from load_core import ensure_columns_exist
                    ensure_columns_exist(self.engine, df, self.table_name, RAW_SCHEMA)

                    conn.execute(text(f'CREATE TEMP TABLE {staging_table} (LIKE "{RAW_SCHEMA}"."{self.table_name}")'))
                    
                    # POSTGRES LIMIT: Avoid parameter overflow
                    df.to_sql(
                        name=staging_table, 
                        con=conn, 
                        if_exists='append', 
                        index=False, 
                        method='multi', # Multi is safe if chunksize is small
                        chunksize=50
                    )
                    
                    cols = [f'"{c}"' for c in df.columns]
                    conn.execute(text(f"""
                        INSERT INTO "{RAW_SCHEMA}"."{self.table_name}" ({', '.join(cols)})
                        SELECT {', '.join(cols)} FROM {staging_table}
                        ON CONFLICT ("hash_id") DO NOTHING
                    """))
                self.total_ingested += len(df)
                # ATOMIC CHECKPOINT: Update progress after successful commit
                self._update_metadata(source_key, n_offset, n_watermark)
                logger.info(f"WRITER: Persisted {len(df)} rows. Mode: {mode}. Checkpoint: {n_watermark} @ {n_offset}. Global Total: {self.total_ingested}")
            except Exception as e: 
                logger.error(f"WRITER ERROR: {e}\n{traceback.format_exc()}")
                self.fatal_error = e
                self.stop_event.set() # Stop fetchers
            finally: self.queue.task_done()

    def run_sync(self, reset=False, backfill_years=None, limit=0):
        if reset:
            logger.warning(f"RESET: Cleaning up {self.table_name} for full reconstruction...")
            with self.engine.connect() as conn:
                if self._table_exists():
                    conn.execute(text(f'TRUNCATE TABLE "{RAW_SCHEMA}"."{self.table_name}" CASCADE'))
                conn.execute(text(f'DELETE FROM "{RAW_SCHEMA}"."ingestion_metadata"'))
                conn.commit()

        threading.Thread(target=self.writer_worker, name="WriterThread", daemon=True).start()

        dataset_threads = []
        target_datasets = ["SECOP_I", "SECOP_II"]
        self._worker_signals = len(target_datasets)

        for source in target_datasets:
            if backfill_years:
                if source == "SECOP_II":
                    # MEGASTREAM: SECOP II is too large and has too many null dates for Year-Slicing.
                    # We use a single continuous stream to ensure 100% coverage.
                    t = threading.Thread(
                        target=self.fetcher_worker, 
                        args=(source, "backfill", 0, None), 
                        name=f"Global-Stream-{source}"
                    )
                    t.start()
                    dataset_threads.append(t)
                else:
                    # SECOP I: Sparse data with business filters works well with year slices.
                    for yr in backfill_years:
                        date_col = "fecha_de_firma_del_contrato"
                        condition = f"{date_col} between '{yr}-01-01T00:00:00' and '{yr}-12-31T23:59:59'"
                        t = threading.Thread(
                            target=self.fetcher_worker, 
                            args=(source, "backfill", 0, condition), 
                            name=f"Backfill-{source}-{yr}"
                        )
                        t.start()
                        dataset_threads.append(t)
            else:
                # SYNC MODE: Respect scavenge_limit from Dagster config
                t = threading.Thread(target=self.fetcher_worker, args=(source, "sync", limit), name=f"Sync-{source}")
                t.start()
                dataset_threads.append(t)

        for t in dataset_threads: t.join()
        self.queue.join()
        self.queue.put(None)
        
        if self.fatal_error:
            logger.error(f"Sync failed due to fatal error in writer thread: {self.fatal_error}")
            raise self.fatal_error

        self.finalize_sync()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified SECOP Dagster Ingestor")
    parser.add_argument("--reset", action="store_true", help="Truncate table and clear metadata")
    parser.add_argument("--full-backfill", action="store_true", help="Trigger Date-Sliced ingestion for all years")
    parser.add_argument("--test-run", action="store_true", help="Backfill only 2024 for testing")
    parser.add_argument("--scavenge-limit", type=int, default=100000, help="Row limit for the sync process")
    
    args = parser.parse_args()
    streamer = MatrixStreamer()
    
    backfill_range = None
    if args.full_backfill: backfill_range = range(2005, 2026)
    elif args.test_run: backfill_range = [2024]
    
    streamer.run_sync(reset=args.reset, backfill_years=backfill_range, limit=args.scavenge_limit)
