from dagster_dbt import DbtCliResource, dbt_assets
from dagster import AssetKey, file_relative_path, AssetExecutionContext
import json
import os

DBT_PROJECT_DIR = "/app/transform/dbt"

# Initialize dbt resource
dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROJECT_DIR,
)

# Load dbt assets
@dbt_assets(manifest=os.path.join(DBT_PROJECT_DIR, "target", "manifest.json"))
def dbt_project_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
