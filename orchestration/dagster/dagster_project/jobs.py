from dagster import define_asset_job, AssetSelection
from .assets.bronze.secop.assets import SecopConfig

# 1. DAILY SYNC JOB
# Fetches recent updates with a 7-day lookback
secop_daily_sync_job = define_asset_job(
    name="secop_daily_sync_job",
    selection=AssetSelection.assets("raw_secop_contracts"),
    config={
        "ops": {
            "raw_secop_contracts": {
                "config": {
                    "full_backfill": False,
                    "deep_scavenge": False,
                    "scavenge_limit": 100000
                }
            }
        }
    }
)

# 2. WEEKLY BACKFILL JOB
# Re-scans current periods to ensure no silent updates were missed recently
secop_weekly_backfill_job = define_asset_job(
    name="secop_weekly_backfill_job",
    selection=AssetSelection.assets("raw_secop_contracts"),
    config={
        "ops": {
            "raw_secop_contracts": {
                "config": {
                    "full_backfill": True, # Triggers year-based slicing
                    "deep_scavenge": False
                }
            }
        }
    }
)

# 3. QUARTERLY TOTAL VIGILANCE JOB
# Full structural scan of all 8.6M rows using business keys
secop_quarterly_scavenge_job = define_asset_job(
    name="secop_quarterly_scavenge_job",
    selection=AssetSelection.assets("raw_secop_contracts"),
    config={
        "ops": {
            "raw_secop_contracts": {
                "config": {
                    "full_backfill": False,
                    "deep_scavenge": True,
                    "scavenge_limit": 0 # Unlimited
                }
            }
        }
    }
)
