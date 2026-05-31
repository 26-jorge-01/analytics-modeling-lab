from dagster import ScheduleDefinition
from .jobs import (
    secop_daily_sync_job, 
    secop_weekly_backfill_job, 
    secop_quarterly_scavenge_job
)

# Daily Sync at 02:00 AM
secop_daily_schedule = ScheduleDefinition(
    job=secop_daily_sync_job,
    cron_schedule="0 2 * * *",
    execution_timezone="America/Bogota"
)

# Weekly Backfill on Sundays at 04:00 AM
secop_weekly_schedule = ScheduleDefinition(
    job=secop_weekly_backfill_job,
    cron_schedule="0 4 * * 0",
    execution_timezone="America/Bogota"
)

# Quarterly Deep Scavenge on the 1st of Jan, Apr, Jul, Oct at 01:00 AM
secop_quarterly_schedule = ScheduleDefinition(
    job=secop_quarterly_scavenge_job,
    cron_schedule="0 1 1 1,4,7,10 *",
    execution_timezone="America/Bogota"
)
