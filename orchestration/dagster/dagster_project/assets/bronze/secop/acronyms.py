import pandas as pd
import os
from sqlalchemy import create_engine
from dagster import asset, AssetExecutionContext, AssetKey

@asset(
    key=AssetKey(["raw_agency_acronyms"]),
    group_name="bronze",
    description="Loads the manual agency acronym dictionary into the raw database schema.",
    tags={"layer": "bronze", "source": "manual", "domain": "public_procurement"},
    compute_kind="python"
)
def raw_agency_acronyms(context: AssetExecutionContext):
    # Resolve paths
    base_dir = os.getcwd()
    csv_path = os.path.join(base_dir, "ingestion", "data", "agency_acronyms.csv")
    
    if not os.path.exists(csv_path):
        csv_path = "/app/ingestion/data/agency_acronyms.csv"
        
    context.log.info(f"Loading acronyms from {csv_path}")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # --- SCHEMA VALIDATION GAP FIX ---
    # Enforce strict contract for the acronym registry
    REQUIRED_COLUMNS = {"acronym", "expanded_name"}
    missing = REQUIRED_COLUMNS - set(df.columns)
    
    if missing:
        raise ValueError(f"CRITICAL: Acronym CSV is missing required columns: {missing}")
        
    if df["acronym"].isnull().any() or df["expanded_name"].isnull().any():
        raise ValueError("CRITICAL: Acronym dictionary cannot contain null values.")
    # ---------------------------------

    # Connect to PostgreSQL
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_name = os.getenv("POSTGRES_DB", "postgres")
    
    engine = create_engine(f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}")
    
    # Write to RAW schema
    df.to_sql(
        name="agency_acronyms",
        con=engine,
        schema="raw",
        if_exists="replace",
        index=False
    )
    
    context.log.info(f"Successfully loaded {len(df)} acronyms to raw.agency_acronyms")
    return "Success"
