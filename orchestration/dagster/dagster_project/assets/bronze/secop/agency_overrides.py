import pandas as pd
import os
from sqlalchemy import create_engine
from dagster import asset, AssetExecutionContext, AssetKey

@asset(
    key=AssetKey(["raw_agency_overrides"]),
    group_name="bronze",
    description="Loads the manual agency override CSV into the raw database schema.",
    tags={"layer": "bronze", "source": "manual", "domain": "public_procurement"},
    compute_kind="python"
)
def raw_agency_overrides(context: AssetExecutionContext):
    # Resolve paths
    base_dir = os.getcwd()
    csv_path = os.path.join(base_dir, "ingestion", "data", "agency_overrides.csv")
    
    if not os.path.exists(csv_path):
        csv_path = "/app/ingestion/data/agency_overrides.csv"
        
    context.log.info(f"Loading manual overrides from {csv_path}")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # --- SCHEMA VALIDATION GAP FIX ---
    # Define expected contract
    REQUIRED_COLUMNS = {"raw_nit_entidad", "canonical_nit_entidad"}
    missing = REQUIRED_COLUMNS - set(df.columns)
    
    if missing:
        raise ValueError(f"CRITICAL: Override CSV is missing required columns: {missing}")
        
    if df["canonical_nit_entidad"].isnull().any():
        null_rows = df[df["canonical_nit_entidad"].isnull()]
        context.log.error(f"Found null values in canonical_nit_entidad:\n{null_rows}")
        raise ValueError("CRITICAL: canonical_nit_entidad cannot contain null values in the override file.")
    # ---------------------------------

    # Connect to PostgreSQL
    # Dagster usually provides resources, but we fallback to env vars identical to soda/dbt
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_name = os.getenv("POSTGRES_DB", "postgres")
    
    engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}")
    
    # Write to RAW schema
    # Treat it exactly like other raw ingested tables
    df.to_sql(
        name="agency_overrides",
        con=engine,
        schema="raw",
        if_exists="replace",
        index=False
    )
    
    context.log.info(f"Successfully loaded {len(df)} overrides to raw.agency_overrides")
    return "Success"
