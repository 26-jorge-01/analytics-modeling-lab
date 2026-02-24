import os
import json
from dagster_dbt import DbtCliResource, dbt_assets, DagsterDbtTranslator
from dagster import AssetKey, AssetDep, AssetExecutionContext

DBT_PROJECT_DIR = "/app/transform/dbt"

# Initialize dbt resource
dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROJECT_DIR,
)

class CustomDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        return AssetKey([dbt_resource_props["name"]])

    def get_group_name(self, dbt_resource_props):
        fqn = dbt_resource_props.get("fqn", [])
        if len(fqn) >= 3:
            layer = fqn[1]
            return layer if layer in ["staging", "intermediate", "marts"] else "dbt"
        return "dbt"

    def get_asset_spec(self, manifest, unique_id, project):
        # 1. Get the base spec with all standard Dagster logic
        spec = super().get_asset_spec(manifest, unique_id, project)

        # 2. Look up the node properties from the manifest using the unique_id
        # unique_id looks like: "model.modeling_lab.stg_customers" or "source.modeling_lab.olist.customers"
        all_nodes = {**manifest.get("nodes", {}), **manifest.get("sources", {})}
        node = all_nodes.get(unique_id)

        if node is None:
            return spec

        # 3. CIRCUIT BREAKER: inject quality gate dependency
        # Target sources and staging models as the dbt entry points.
        res_type = node.get("resource_type")
        fqn = node.get("fqn", [])

        if res_type == "source" or (res_type == "model" and "staging" in fqn):
            quality_dep = AssetDep(AssetKey(["soda_raw_health"]))
            new_deps = list(spec.deps) + [quality_dep]
            return spec.replace_attributes(deps=new_deps)

        return spec


# Load dbt assets
@dbt_assets(
    manifest=os.path.join(DBT_PROJECT_DIR, "target", "manifest.json"),
    dagster_dbt_translator=CustomDagsterDbtTranslator()
)
def dbt_project_assets(
    context: AssetExecutionContext,
    dbt: DbtCliResource,
):
    yield from dbt.cli(["build"], context=context).stream()
