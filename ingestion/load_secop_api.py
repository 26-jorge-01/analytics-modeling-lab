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
    from ingestion.load_core import (
        get_engine, ensure_schema_exists, dataframe_to_postgres, 
        RAW_SCHEMA, load_file
    )
    from pysecop import SecopClient, QueryBuilder, DATASETS
    from pysecop.utils import normalize_dataframe, get_unified_columns
    from pysecop.utils.helpers import get_mapped_column
except ImportError as e:
    logger.error(f"Failed to import dependencies: {e}")
    sys.exit(1)

def sanitize_db_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strictly Postgres-safe column name sanitization (max 63 chars)."""
    def _normalize(c):
        c = "".join(ch for ch in unicodedata.normalize('NFKD', str(c)) if not unicodedata.combining(ch))
        c = re.sub(r'[^a-zA-Z0-9]', '_', c).lower()
        c = re.sub(r'_+', '_', c).strip('_')
        return c[:63]
    df.columns = [_normalize(c) for c in df.columns]
    # Drop socrata-specific hidden columns early
    cols_to_drop = [c for c in df.columns if c.startswith('id_') and len(c) < 5 or c in ['id', 'uid', 'id_']]
    df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
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
        all_cols = sorted(list(set(unified_cols + tech_cols)))
        
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
    def _create_table(self, df=None):
        logger.info(f"Target table {RAW_SCHEMA}.{self.table_name} not found. Creating Snapshot structure...")
        
        unified_cols = get_unified_columns()
        tech_cols = ["source", "hash_id", "ingested_at", "socrata_id"]
        all_cols = sorted(list(set(unified_cols + tech_cols)))
        
        schema_df = pd.DataFrame(columns=all_cols)
        schema_df.to_sql(name=self.table_name, con=self.engine, schema=RAW_SCHEMA, if_exists='replace', index=False)
        
        # 4. Add Primary Key on Business Key for Snapshot logic
        with self.engine.begin() as conn:
            conn.execute(text(f'ALTER TABLE "{RAW_SCHEMA}"."{self.table_name}" ADD PRIMARY KEY (source, id_contrato, nit_entidad)'))
            # Attach the Audit Trigger
            conn.execute(text(f"""
                DROP TRIGGER IF EXISTS trg_audit_secop ON "{RAW_SCHEMA}"."{self.table_name}";
                CREATE TRIGGER trg_audit_secop
                BEFORE UPDATE ON "{RAW_SCHEMA}"."{self.table_name}"
                FOR EACH ROW EXECUTE FUNCTION raw.audit_secop_changes();
            """))
            
        logger.info(f"Unified Snapshot table {RAW_SCHEMA}.{self.table_name} created.")

    def finalize_sync(self):
        """Indexes and maintenance."""
        if self.fatal_error: raise self.fatal_error
        if not self._table_exists(): return

        with self.engine.connect() as conn:
            logger.info("MAINTENANCE: Creating performance indexes...")
            conn.execute(text(f'CREATE INDEX IF NOT EXISTS idx_secop_hash ON "{RAW_SCHEMA}"."{self.table_name}" (hash_id)'))
            conn.execute(text(f'CREATE INDEX IF NOT EXISTS idx_secop_audit_lookup ON "{RAW_SCHEMA}"."{self.table_name}" (source, id_contrato, nit_entidad)'))
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
            # We use historical_offset as a generic string storage for the last_id if it's not a number
            row = conn.execute(text(f'SELECT historical_offset_val, historical_watermark FROM "{RAW_SCHEMA}"."ingestion_metadata" WHERE source = :s'), {"s": source_key}).fetchone()
            return (row[0], row[1]) if row else (None, None)

    def _update_metadata(self, source_key, last_id, watermark):
        with self.engine.connect() as conn:
            query = f"""
                INSERT INTO "{RAW_SCHEMA}"."ingestion_metadata" (source, historical_offset_val, historical_watermark, last_run)
                VALUES (:s, :o, :w, CURRENT_TIMESTAMP)
                ON CONFLICT (source) DO UPDATE SET 
                    historical_offset_val = EXCLUDED.historical_offset_val, 
                    historical_watermark = EXCLUDED.historical_watermark,
                    last_run = CURRENT_TIMESTAMP
            """
            conn.execute(text(query), {"s": source_key, "o": str(last_id), "w": watermark})
            conn.commit()

    def make_hash(self, row):
        """Zero-Loss Deterministic Hashing using Stable Business Keys."""
        try:
            ident_parts = [
                str(row.get('source', '')).strip().upper(),
                str(row.get('id_contrato', '')).strip().upper(),
                str(row.get('proceso_de_compra', '')).strip().upper(),
                str(row.get('nit_entidad', '')).strip().upper()
            ]
            
            # Watermark: Use the update timestamp if available
            ua = row.get('ultima_actualizacion')
            ua_str = '1900-01-01T00:00:00.000000'
            if pd.notnull(ua):
                try: ua_str = pd.to_datetime(ua).strftime('%Y-%m-%dT%H:%M:%S.%f')
                except: pass
            ident_parts.append(ua_str)
            
            identity = "|".join(ident_parts)
            
            # Exclude technical metadata from the content fingerprint
            exclude = {'hash_id', 'ingested_at', 'id', 'uid', 'socrata_id'}
            content_row = {str(k): str(v) for k, v in row.items() if k not in exclude}
            content_str = json.dumps(content_row, sort_keys=True)
            
            return hashlib.md5(f"{identity}||{content_str}".encode('utf-8')).hexdigest()
        except:
            return hashlib.md5(str(row).encode('utf-8')).hexdigest()

    def fetcher_worker(self, source_label, mode="sync", limit=0, date_filter=None, deep_scavenge=False):
        """
        Hyper-Careful Fetcher:
        - Uses id_contrato (Business Key) as a stable keyset cursor to bypass OFFSET limits.
        - If deep_scavenge=True, ignores timestamps and scans the entire dataset by ID to find silent changes.
        """
        from pysecop import QueryBuilder
        
        logger.info(f"FETCHER ({source_label} - {mode}): Starting hyper-careful scan...")
        api_source = source_label.replace('_', ' ')
        search_limit = 50000 
        ua_col = get_mapped_column(source_label, "ultima_actualizacion")
        id_col = get_mapped_column(source_label, "id_contrato")
        
        # Paging state recovery
        state_key = f"{source_label}:cursor" if not date_filter else f"{source_label}:{date_filter}:cursor"
        last_business_id, _ = self._get_metadata(state_key)
        
        total_fetched_this_source = 0
        logger.info(f"FETCHER ({source_label}): Resuming from Business ID cursor: {last_business_id}")
        
        while not self.stop_event.is_set():
            try:
                qb = QueryBuilder()
                qb.select(["*", ":id"]) 
                
                # BASE FILTERS (Business Rules)
                if source_label == "SECOP_I":
                    qb.where_custom("upper(estado_del_proceso) = 'ADJUDICADO'")

                # HYPER-CAREFUL LOGIC
                if deep_scavenge:
                    # Ignore timestamps, use only the ID cursor to find silent ghosts
                    if last_business_id:
                        qb.where_custom(f"{id_col} > '{last_business_id}'")
                elif mode == "sync":
                    # Standard sync with a 7-day "Lookback Window" to catch delayed updates
                    lookback_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
                    qb.where_custom(f"{ua_col} >= '{lookback_date}'")
                    if last_business_id:
                         qb.where_custom(f"{id_col} > '{last_business_id}'")
                elif mode == "backfill" and date_filter:
                    qb.where_custom(date_filter)
                    if last_business_id:
                        qb.where_custom(f"{id_col} > '{last_business_id}'")
                
                # Stable Keyset Paging on Business ID
                qb.order(id_col, "ASC") 
                qb.limit(search_limit)

                # Fetch batch
                df = self.client.fetch(source_label, qb, content_type="json")
                if df.empty: break
                
                # Robust Date Handling
                df[ua_col] = pd.to_datetime(df[ua_col], errors='coerce')
                df[ua_col] = df[ua_col].fillna(pd.Timestamp("1900-01-01"))
                
                # Update Cursor
                last_business_id = df[id_col].iloc[-1]
                
                logger.info(f"FETCHER ({source_label}): Progressed to Business ID {last_business_id}. Batch size: {len(df)}")
                
                # Processing
                df['source'] = api_source
                df = normalize_dataframe(df, source_label)
                df = sanitize_db_columns(df) # Early sanitization
                df = serialize_complex_vectorized(df)
                
                # Generate unique Hash ID (Includes all columns, so it detects "Silent Updates")
                df['hash_id'] = df.apply(self.make_hash, axis=1)
                df['ingested_at'] = datetime.now()
                
                # Update metadata with the Business ID cursor
                self.queue.put((state_key, mode, last_business_id, df[ua_col].max(), df))
                total_fetched_this_source += len(df)
                
                if limit > 0 and total_fetched_this_source >= limit: break
                if len(df) < search_limit: break
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"FETCHER ERROR ({source_label}): {e}")
                time.sleep(10) # Longer wait on error to be careful with API limits


    def writer_worker(self):
        """Consumer: Atomic Business-Key UPSERT to Postgres."""
        from sqlalchemy.dialects.postgresql import insert
        
        while True:
            item = self.queue.get()
            if item is None: break
            source_key, mode, n_cursor, n_watermark, df = item
            try:
                if not self._table_exists():
                    self._create_table(df)
                
                # Dynamic column discovery for UPSERT
                target_table = f'"{RAW_SCHEMA}"."{self.table_name}"'
                
                # Use a more robust upsert method
                with self.engine.begin() as conn:
                    from load_core import ensure_columns_exist
                    ensure_columns_exist(self.engine, df, self.table_name, RAW_SCHEMA)
                    
                    # DIRTY DATA SHIELD: PK columns cannot be NULL
                    for col in ['source', 'id_contrato', 'nit_entidad']:
                        if col in df.columns:
                            df[col] = df[col].fillna(f'UNKNOWN_{col.upper()}').astype(str)
                    
                    # IDENTITY GUARD: Deduplicate within the batch to prevent CardinalityViolation
                    df.drop_duplicates(subset=['source', 'id_contrato', 'nit_entidad'], keep='last', inplace=True)
                    
                    # Prepare the data for chunked bulk upsert
                    chunk_size = 500
                    data_list = df.to_dict(orient='records')
                    
                    from sqlalchemy import MetaData, Table
                    metadata = MetaData()
                    table = Table(self.table_name, metadata, autoload_with=self.engine, schema=RAW_SCHEMA)
                    
                    for i in range(0, len(data_list), chunk_size):
                        chunk = data_list[i:i + chunk_size]
                        if not chunk: continue
                        
                        stmt = insert(table).values(chunk)
                        update_cols = {c.name: c for c in stmt.excluded if c.name not in ['source', 'id_contrato', 'nit_entidad']}
                        
                        upsert_stmt = stmt.on_conflict_do_update(
                            index_elements=['source', 'id_contrato', 'nit_entidad'],
                            set_=update_cols,
                            where=(table.c.hash_id != stmt.excluded.hash_id)
                        )
                        conn.execute(upsert_stmt)
                    
                self.total_ingested += len(df)
                self._update_metadata(source_key, n_cursor, n_watermark)
                logger.info(f"WRITER: Snapshot Upsert complete for {len(df)} rows. Total: {self.total_ingested}")
            except Exception as e: 
                logger.error(f"WRITER ERROR: {e}")
                self.fatal_error = e
                self.stop_event.set() 
            finally: self.queue.task_done()

    def run_sync(self, reset=False, backfill_years=None, limit=0, deep_scavenge=False):
        if reset:
            logger.warning(f"RESET: Cleaning up {self.table_name}...")
            with self.engine.connect() as conn:
                if self._table_exists():
                    conn.execute(text(f'TRUNCATE TABLE "{RAW_SCHEMA}"."{self.table_name}" CASCADE'))
                conn.execute(text(f'DELETE FROM "{RAW_SCHEMA}"."ingestion_metadata"'))
                conn.commit()

        threading.Thread(target=self.writer_worker, name="WriterThread", daemon=True).start()

        dataset_threads = []
        target_datasets = ["SECOP_I", "SECOP_II"]

        for source in target_datasets:
            if deep_scavenge:
                # TOTAL VIGILANCE: Full business-key scan
                t = threading.Thread(
                    target=self.fetcher_worker, 
                    args=(source, "backfill", 0, None, True), 
                    name=f"DeepScan-{source}"
                )
                t.start()
                dataset_threads.append(t)
            elif backfill_years:
                # SLICED BACKFILL: Year-based slices + NULL Date Pass
                date_col = get_mapped_column(source, "fecha_de_firma")
                
                # 1. Standard Year Slices
                for i in range(0, len(backfill_years), 4):
                    batch = backfill_years[i:i+4]
                    batch_threads = []
                    for yr in batch:
                        t = threading.Thread(
                            target=self.fetcher_worker, 
                            args=(source, "backfill", 0, f"{date_col} between '{yr}-01-01' and '{yr}-12-31'"), 
                            name=f"Backfill-{source}-{yr}"
                        )
                        t.start()
                        batch_threads.append(t)
                        dataset_threads.append(t)
                    
                    for t in batch_threads: t.join()
                
                # 2. NULL Date Pass: Catch records that have no signature date but exist in API
                logger.info(f"BACKFILL ({source}): Starting NULL date recovery pass...")
                t_null = threading.Thread(
                    target=self.fetcher_worker,
                    args=(source, "backfill", 0, f"{date_col} is null"),
                    name=f"Backfill-{source}-NULLS"
                )
                t_null.start()
                dataset_threads.append(t_null)
                t_null.join()
            else:
                # INCREMENTAL SYNC
                t = threading.Thread(target=self.fetcher_worker, args=(source, "sync", limit), name=f"Sync-{source}")
                t.start()
                dataset_threads.append(t)

        for t in dataset_threads: t.join()
        self.queue.join()
        self.queue.put(None)
        
        if self.fatal_error: raise self.fatal_error
        self.finalize_sync()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified SECOP Hyper-Careful Ingestor")
    parser.add_argument("--reset", action="store_true", help="Truncate table and clear metadata")
    parser.add_argument("--full-backfill", action="store_true", help="Trigger Full Historical Reconstruction")
    parser.add_argument("--deep-scavenge", action="store_true", help="Perform full-dataset scan for silent updates")
    parser.add_argument("--scavenge-limit", type=int, default=0, help="Row limit (0 for unlimited)")
    
    args = parser.parse_args()
    streamer = MatrixStreamer()
    
    backfill_range = None
    if args.full_backfill: 
        # range(2000, 2027) covers 2000 to 2026 (current year)
        backfill_range = range(2000, 2030)
    
    streamer.run_sync(
        reset=args.reset, 
        backfill_years=backfill_range, 
        limit=args.scavenge_limit,
        deep_scavenge=args.deep_scavenge
    )
