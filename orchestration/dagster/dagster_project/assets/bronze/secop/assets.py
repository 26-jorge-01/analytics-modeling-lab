import subprocess
from dagster import asset, AssetExecutionContext, AssetKey, Config

class SecopConfig(Config):
    full_backfill: bool = False
    scavenge_limit: int = 100000

@asset(
    key=AssetKey(["raw_secop_api"]),
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
    compute_kind="python"
)
def raw_secop_api_load(context: AssetExecutionContext, config: SecopConfig):
    # Ingestion script path
    load_secop_path = "/app/ingestion/load_secop_api.py"

    context.log.info(f"Starting raw SECOP ingestion (Full: {config.full_backfill}, Scavenge Limit: {config.scavenge_limit})...")

    # Command construction - aligned with MatrixStreamer
    cmd = ["python", load_secop_path, "--scavenge-limit", str(config.scavenge_limit)]
    if config.full_backfill:
        cmd.append("--full-backfill")

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
