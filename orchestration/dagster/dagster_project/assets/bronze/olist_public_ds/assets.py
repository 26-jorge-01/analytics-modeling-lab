import subprocess
from dagster import asset, AssetExecutionContext

@asset
def raw_load(context: AssetExecutionContext):
    """
    Ingests raw data from CSV files and generates synthetic data.
    Runs extract_load.py and generate_synthetic.py.
    """
    # Ingestion script path
    extract_load_path = "/app/ingestion/extract_load.py"
    generate_synthetic_path = "/app/ingestion/generate_synthetic.py"
    
    context.log.info("Starting raw data ingestion...")
    
    # Run extract_load.py
    try:
        subprocess.run(["python", extract_load_path], check=True, capture_output=True, text=True)
        context.log.info("extract_load.py executed successfully.")
    except subprocess.CalledProcessError as e:
        context.log.error(f"Error running extract_load.py: {e.stderr}")
        raise e

    # Run generate_synthetic.py
    try:
        subprocess.run(["python", generate_synthetic_path], check=True, capture_output=True, text=True)
        context.log.info("generate_synthetic.py executed successfully.")
    except subprocess.CalledProcessError as e:
        context.log.error(f"Error running generate_synthetic.py: {e.stderr}")
        raise e

    return "Success"