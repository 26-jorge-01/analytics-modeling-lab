from dagster import Definitions, load_assets_from_modules
from .assets.bronze.secop import assets as bronze_secop_assets
from .assets.bronze.secop import agency_overrides as agency_overrides_assets
from .assets.bronze.secop import acronyms as acronyms_assets
from .assets.bronze.secop import location_homologation as location_homologation_assets
from .assets import dbt as dbt_assets_module
from .assets import metrics as metrics_assets
from .assets import quality as quality_assets

from .jobs import (
    secop_daily_sync_job, 
    secop_weekly_backfill_job, 
    secop_quarterly_scavenge_job
)
from .schedules import (
    secop_daily_schedule, 
    secop_weekly_schedule, 
    secop_quarterly_schedule
)

# Load all assets
all_assets = [
    *load_assets_from_modules([bronze_secop_assets, agency_overrides_assets, acronyms_assets, location_homologation_assets]),
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
    jobs=[
        secop_daily_sync_job, 
        secop_weekly_backfill_job, 
        secop_quarterly_scavenge_job
    ],
    schedules=[
        secop_daily_schedule, 
        secop_weekly_schedule, 
        secop_quarterly_schedule
    ],
)
