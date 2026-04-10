from dagster import Definitions, load_assets_from_modules
from .assets.bronze.secop import assets as bronze_secop_assets
from .assets import dbt as dbt_assets_module
from .assets import metrics as metrics_assets
from .assets import quality as quality_assets

# Load all assets
all_assets = [
    *load_assets_from_modules([bronze_secop_assets]),
    dbt_assets_module.dbt_project_assets,
    *load_assets_from_modules([metrics_assets, quality_assets]),
]

# Define resources
resources = {
    "dbt": dbt_assets_module.dbt_resource,
}

defs = Definitions(
    assets=all_assets,
    resources=resources,
)
