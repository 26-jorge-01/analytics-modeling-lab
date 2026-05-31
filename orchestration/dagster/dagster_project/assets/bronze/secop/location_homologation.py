import pandas as pd
import os
from sqlalchemy import create_engine
from dagster import asset, AssetExecutionContext, AssetKey

@asset(
    key=AssetKey(["raw_location_homologation"]),
    group_name="bronze",
    description="Loads the manual location homologation CSV into the raw database schema.",
    tags={"layer": "bronze", "source": "manual", "domain": "geography"},
    compute_kind="python"
)
def raw_location_homologation(context: AssetExecutionContext):
    # Resolve paths
    base_dir = os.getcwd()
    csv_path = os.path.join(base_dir, "ingestion", "data", "location_homologation.csv")
    
    if not os.path.exists(csv_path):
        csv_path = "/app/ingestion/data/location_homologation.csv"
        
    context.log.info(f"Loading location homologation from {csv_path}")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Validation
    REQUIRED_COLUMNS = {"raw_location_name", "target_location_name"}
    missing = REQUIRED_COLUMNS - set(df.columns)
    
    if missing:
        raise ValueError(f"CRITICAL: Location Homologation CSV is missing required columns: {missing}")
        
    # Connect to PostgreSQL
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_name = os.getenv("POSTGRES_DB", "postgres")
    
    engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}")
    
    from sqlalchemy import text
    
    # Write to RAW schema with TRUNCATE + APPEND strategy
    with engine.begin() as conn:
        exists_query = text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'raw' AND table_name = 'location_homologation')")
        table_exists = conn.execute(exists_query).scalar()
        
        if table_exists:
            context.log.info("Table raw.location_homologation exists. Checking for schema updates.")
            
            # Schema Evolution
            for column in df.columns:
                col_exists_query = text(f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_schema = 'raw' AND table_name = 'location_homologation' AND column_name = '{column}')")
                if not conn.execute(col_exists_query).scalar():
                    context.log.info(f"Adding missing column '{column}' to raw.location_homologation")
                    conn.execute(text(f'ALTER TABLE raw.location_homologation ADD COLUMN "{column}" TEXT'))
            
            context.log.info("Truncating and appending data.")
            conn.execute(text("TRUNCATE TABLE raw.location_homologation"))
            df.to_sql(
                name="location_homologation",
                con=conn,
                schema="raw",
                if_exists="append",
                index=False
            )
        else:
            context.log.info("Table raw.location_homologation does not exist. Performing initial load.")
            df.to_sql(
                name="location_homologation",
                con=conn,
                schema="raw",
                if_exists="replace",
                index=False
            )
    
    context.log.info(f"Successfully loaded {len(df)} records to raw.location_homologation")
    return "Success"
