import sys
import traceback
import logging
from logging import getLogger, INFO, FileHandler, StreamHandler
import re
import pandas as pd
import json
import time
import requests
from requests.exceptions import ConnectionError, Timeout
from sqlalchemy.types import Text

# Configure logging
log_file = "/app/ingestion/api_debug_internal.log"
logger = getLogger(__name__)
logger.setLevel(INFO)

# Clear existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

# File handler
fh = FileHandler(log_file, mode='w')
fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(fh)

# Stream handler
sh = StreamHandler(sys.stdout)
sh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(sh)

try:
    from load_core import get_engine, ensure_schema_exists, RAW_SCHEMA, clean_table_name
    from pysecop import SecopClient, QueryBuilder, config
except ImportError as e:
    logger.error(f"Failed to import dependencies: {e}")
    sys.exit(1)

def clean_col(c):
    """Postgres-safe column name cleaning."""
    c = str(c).lower().strip()
    c = c.replace(" ", "_").replace("-", "_").replace(".", "_")
    c = re.sub(r'[^a-z0-9_]', '', c)
    return c[:60]

def serialize_complex(val):
    """Serializes dicts and lists to JSON strings."""
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return val

def fetch_with_retries(client, dataset_id, query_builder, max_retries=10, base_delay=5):
    """
    Fetches data from SECOP API with exponential backoff retries for connection issues.
    """
    for attempt in range(max_retries):
        try:
            return client.fetch(dataset_id, query_builder)
        except (ConnectionError, Timeout, Exception) as e:
            # Check if it's a DNS/Connection error specifically
            is_connection_error = isinstance(e, (ConnectionError, Timeout))
            # Some NameResolutionErrors are wrapped in generic Exception or specific urllib3 ones
            error_str = str(e).lower()
            if not is_connection_error and ("name" not in error_str and "resolve" not in error_str and "connection" not in error_str):
                # If it doesn't look like a transient network error, re-raise immediately
                raise e
            
            wait_time = base_delay * (2 ** attempt)
            if attempt < max_retries - 1:
                logger.warning(f"Connection error: {e}. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries reached. Failing after {max_retries} attempts.")
                raise e

if __name__ == "__main__":
    logger.info("Starting SECOP API ingestion (Robust mode)...")
    try:
        client = SecopClient()
        table_name = "raw_secop_api_contracts"
        
        limit = 10000
        offset = 0
        batch_index = 0
        
        from load_core import dataframe_to_postgres, get_engine, ensure_schema_exists, RAW_SCHEMA
        
        engine = get_engine()
        ensure_schema_exists(engine, RAW_SCHEMA)

        logger.info(f"Starting paginated ingestion (Page size: {limit})...")
        
        while True:
            qb = QueryBuilder()
            qb.select(config.SECOP_II_CONTRATOS.columns) \
              .where_custom("nit_entidad = '899999239'") \
              .limit(limit) \
              .offset(offset)

            logger.info(f"Fetching page {batch_index + 1} (Offset: {offset})...")
            df = fetch_with_retries(client, "SECOP_II", qb)
            
            if df is None or df.empty:
                logger.info("No more data to fetch.")
                break
                
            logger.info(f"Fetched {len(df)} records.")
            
            # Clean columns
            df.columns = [clean_col(c) for c in df.columns]
            
            # STRINGIFY COMPLEX TYPES
            for col in df.columns:
                df[col] = df[col].apply(serialize_complex)
            
            # Database load
            try:
                dataframe_to_postgres(
                    df=df,
                    table_name=table_name,
                    schema=RAW_SCHEMA,
                    if_exists='replace' if batch_index == 0 else 'append',
                    batch_index=batch_index
                )
                logger.info(f"Page {batch_index + 1} loaded successfully.")
            except Exception as sql_e:
                logger.error(f"Error loading page {batch_index + 1}:")
                logger.error(traceback.format_exc())
                raise sql_e
                
            if len(df) < limit:
                logger.info("Fetched last page.")
                break
                
            offset += limit
            batch_index += 1

        logger.info("SUCCESS! Full data loaded from SECOP II API.")
            
    except Exception as e:
        logger.error("FATAL ERROR in SECOP API ingestion script:")
        logger.error(traceback.format_exc())
        sys.exit(1)

    logger.info("Script finished successfully.")