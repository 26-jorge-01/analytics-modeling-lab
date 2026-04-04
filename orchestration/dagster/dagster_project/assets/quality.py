import subprocess
from dagster import asset, AssetExecutionContext, AssetKey, Failure

SODA_PATH = "/app/quality/soda"
SODA_BINARY = "/usr/local/bin/soda"


def run_soda_scan(
    context, checks_file: str, layer_name: str, data_source: str = "postgres"
) -> str:
    cmd = [
        SODA_BINARY, "scan",
        "-d", data_source,
        "-c", f"{SODA_PATH}/configuration.yml",
        f"{SODA_PATH}/{checks_file}",
        "--verbose",
    ]

    context.log.info(f"Running Soda: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Log ALWAYS
    context.log.info(f"Soda exit code: {result.returncode}")
    if result.stdout:
        context.log.info("Soda STDOUT:\n" + result.stdout)
    if result.stderr:
        context.log.error("Soda STDERR:\n" + result.stderr)

    # Decide what to do based on return code
    if result.returncode == 0:
        context.log.info(f"Soda {layer_name} scan completed successfully.")
        return result.stdout

    # 1/2/3/4 = non-zero => fail the op (circuit breaker)
    raise Failure(
        description=(
            f"Soda {layer_name} scan failed with exit code "
            f"{result.returncode}. See logs above for details."
        ),
        metadata={
            "soda_exit_code": result.returncode,
            "layer": layer_name,
        },
    )


@asset(
    group_name="quality",
    deps=["raw_secop_api"],
    compute_kind="soda",
    tags={
        "domain": "data_quality",
        "context": "raw_health"
    }
)
def soda_raw_health(context: AssetExecutionContext):
    """
    CRITICAL: Circuit Breaker for ingested data.
    Ensures raw data is healthy BEFORE dbt starts building.
    """
    stdout = run_soda_scan(context, 'checks_raw.yml', "RAW", "raw")
    context.add_output_metadata({"soda_report": stdout, "layer": "raw"})
    return "Raw Health Verified"