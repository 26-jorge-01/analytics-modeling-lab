import subprocess
from dagster import asset, AssetExecutionContext, AssetKey

@asset(
    key=AssetKey(["raw_secop_api"]),
    group_name="bronze",
    description="""
    Ingests raw data from SECOP API.
    This asset executes:
    1. load_secop_api.py: Loads source SECOP API into the raw database schema.
    """,
    tags={
        "layer": "bronze",
        "source": "secop",
        "domain": "public_procurement",
        "entity": "contracts"
    },
    compute_kind="python"
)
def raw_secop_api_load(context: AssetExecutionContext):
    # Ingestion script path
    load_secop_path = "/app/ingestion/load_secop_api.py"

    context.log.info("Starting raw secop data ingestion...")

    # Run load_secop.py
    try:
        result = subprocess.run(
            ["python", load_secop_path], 
            check=True,
            text=True,
            capture_output=True
        )
        context.log.info("load_secop_api.py executed successfully.")
        context.log.debug(result.stdout)
    except subprocess.CalledProcessError as e:
        context.log.error(f"Error running load_secop_api.py (Exit Code {e.returncode}):")
        context.log.error(f"STDOUT: {e.stdout}")
        context.log.error(f"STDERR: {e.stderr}")
        raise e

    return "Success"
