import subprocess
from dagster import asset, AssetExecutionContext, AssetKey, Config, RetryPolicy, Backoff

import os

class SecopConfig(Config):
    full_backfill: bool = True
    reset: bool = False
    scavenge_limit: int = 10000000 # Default to 10M for totality

@asset(
    key=AssetKey(["raw_secop_contracts"]),
    group_name="bronze",
    description="""
    Ingests raw data from SECOP API into a Unified Matrix.
    Implements a High-Performance Parallel Ingestor with 
    Incremental Frontier and Historical Scavenger Sync.
    """,
    tags={
        "layer": "bronze",
        "source": "secop",
        "domain": "public_procurement",
        "entity": "contracts"
    },
    compute_kind="python",
    retry_policy=RetryPolicy(
        max_retries=10,
        delay=30,
        backoff=Backoff.EXPONENTIAL
    )
)
def raw_secop_api_load(context: AssetExecutionContext, config: SecopConfig):
    # Resolve script path dynamically for both local and container environments
    # Default to local path if not in container
    base_dir = os.getcwd()
    load_secop_path = os.path.join(base_dir, "ingestion", "load_secop_api.py")
    
    if not os.path.exists(load_secop_path):
        # Fallback to absolute container path if needed
        load_secop_path = "/app/ingestion/load_secop_api.py"

    context.log.info(f"Starting raw SECOP ingestion (Full: {config.full_backfill}, Reset: {config.reset}, Scavenge Limit: {config.scavenge_limit})...")

    # Command construction - aligned with MatrixStreamer
    cmd = ["python", load_secop_path, "--scavenge-limit", str(config.scavenge_limit)]
    
    if config.full_backfill:
        cmd.append("--full-backfill")
    
    if config.reset:
        cmd.append("--reset")

    # Run load_secop.py
    try:
        result = subprocess.run(
            cmd, 
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
