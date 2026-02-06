from dagster import Definitions, asset

@asset
def hello_modeling_lab() -> str:
    return "Dagster is running ✅"

defs = Definitions(assets=[hello_modeling_lab])
