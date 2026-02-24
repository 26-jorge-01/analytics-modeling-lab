import os
import subprocess
from dagster import asset, AssetExecutionContext, AssetKey

SODA_PATH = "/app/quality/soda"
SODA_BINARY = "/usr/local/bin/soda"

def run_soda_scan(context, layer_name):
    """Helper to run a tagged Soda scan."""
    context.log.info(f"Starting Soda.io scan for {layer_name} layer...")
    
    # We use -f to filter for specific checks tagged with the layer
    # Note: Soda core currently uses 'include' or just filtering by checks file
    # For this implementation, we will use separate check files or filter by check type
    # but to keep it simple and robust, we will use the 'attributes' filter if supported
    # or just run the full scan and report specific metadata.
    
    cmd = [
        SODA_BINARY, "scan",
        "-d", "postgres",
        "-c", f"{SODA_PATH}/configuration.yml",
        f"{SODA_PATH}/checks.yml"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        context.log.info(f"Soda exit code: {result.returncode}")
        if result.stdout:
            context.log.info("Soda STDOUT:\n" + result.stdout)
        if result.stderr:
            context.log.error("Soda STDERR:\n" + result.stderr)

        result.check_returncode()  # aquí recién “revienta” con detalle ya logueado
        return result.stdout
    
        context.log.info(f"Soda {layer_name} scan completed successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        context.log.error(f"Soda {layer_name} scan failed.")
        raise e

@asset(
    group_name="quality",
    deps=["raw_load"], # Depends on ingestion
)
def soda_raw_health(context: AssetExecutionContext):
    """
    CRITICAL: Circuit Breaker for ingested data.
    Ensures raw data is healthy BEFORE dbt starts building.
    """
    stdout = run_soda_scan(context, "RAW")
    context.add_output_metadata({"soda_report": stdout, "layer": "raw"})
    return "Raw Health Verified"

@asset(
    group_name="quality",
    deps=[AssetKey(["fct_order_item"])],
)
def soda_marts_health(context: AssetExecutionContext):
    """
    Business Health Check. 
    Final verification of Marts before BI consumption.
    """
    stdout = run_soda_scan(context, "MARTS")
    context.add_output_metadata({"soda_report": stdout, "layer": "marts"})
    return "Marts Health Verified"
