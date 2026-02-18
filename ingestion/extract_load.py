import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database Configuration (Defaults for local Docker environment)
DB_USER = os.getenv("POSTGRES_USER", "demo")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "demo")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")  # Use 'postgres' if running inside Docker
DB_PORT = os.getenv("POSTGRES_PORT", "15432")
DB_NAME = os.getenv("POSTGRES_DB", "modeling_lab")

RAW_SCHEMA = "raw"
DATA_DIR = Path("/app/data/brz/olistbr/olist-public-dataset")

def get_engine():
    """Creates a SQLAlchemy engine for the Postgres database."""
    conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(conn_str)

def ensure_schema_exists(engine, schema_name):
    """Ensures that the specified schema exists in the database."""
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        conn.commit()
    logger.info(f"Schema '{schema_name}' verified/created.")

def clean_table_name(filename):
    """
    Cleans the CSV filename to derive a clean table name.
    Example: olist_customers_dataset.csv -> customers
    """
    name = filename.replace("olist_", "").replace("_dataset", "").replace(".csv", "")
    return name

def load_csv_to_postgres():
    """Main function to load CSV files into the Postgres raw schema."""
    if not DATA_DIR.exists():
        # Fallback for local development if /app isn't mounted
        local_data_dir = Path("data/brz/olistbr/olist-public-dataset")
        if local_data_dir.exists():
            data_path = local_data_dir
        else:
            logger.error(f"Data directory {DATA_DIR} not found.")
            return
    else:
        data_path = DATA_DIR

    engine = get_engine()
    
    try:
        ensure_schema_exists(engine, RAW_SCHEMA)
    except Exception as e:
        logger.error(f"Failed to connect or create schema: {e}")
        return

    csv_files = list(data_path.glob("*.csv"))
    
    if not csv_files:
        logger.warning(f"No CSV files found in {data_path}")
        return

    logger.info(f"Found {len(csv_files)} CSV files to load.")

    for file_path in csv_files:
        table_name = clean_table_name(file_path.name)
        logger.info(f"Loading {file_path.name} into {RAW_SCHEMA}.{table_name}...")
        
        try:
            # Load with pandas
            # Note: Geolocation file is large, using low_memory=False to avoid type warnings
            df = pd.read_csv(file_path, low_memory=False)
            
            # Write to SQL
            df.to_sql(
                name=table_name,
                con=engine,
                schema=RAW_SCHEMA,
                if_exists="replace",
                index=False
            )
            logger.info(f"Successfully loaded {len(df)} rows into {RAW_SCHEMA}.{table_name}.")
            
        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}")

if __name__ == "__main__":
    load_csv_to_postgres()
