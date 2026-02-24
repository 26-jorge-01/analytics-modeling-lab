import os
import json
import logging
from pathlib import Path
from dagster import asset, AssetExecutionContext
from sqlalchemy import create_engine, text

# Configure logging
logger = logging.getLogger(__name__)

DBT_TARGET_DIR = Path("/app/transform/dbt/target")


def get_db_engine():
    user = os.getenv("POSTGRES_USER", "demo")
    password = os.getenv("POSTGRES_PASSWORD", "demo")
    db = os.getenv("POSTGRES_DB", "modeling_lab")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(conn_str)


@asset(
    group_name="ops",
    deps=["fct_order_item"]
)
def refresh_metrics(context: AssetExecutionContext):
    """
    Professional metrics refresh: Captures dbt test results
    and table statistics.
    """
    engine = get_db_engine()
    run_id = context.run_id

    # 1. Capture dbt run results
    run_results_path = DBT_TARGET_DIR / "run_results.json"
    dbt_results_data = []

    if run_results_path.exists():
        try:
            with open(run_results_path, "r") as f:
                data = json.load(f)
                for result in data.get("results", []):
                    dbt_results_data.append({
                        "run_id": run_id,
                        "unique_id": result.get("unique_id"),
                        "status": result.get("status"),
                        "execution_time": result.get("execution_time"),
                        # Truncate message
                        "message": str(result.get("message", ""))[:500]
                    })
            context.log.info(f"Parsed {len(dbt_results_data)} dbt results.")
        except Exception as e:
            context.log.error(f"Failed to parse dbt results: {e}")
    else:
        context.log.warning(
            f"dbt run_results.json not found at {run_results_path}"
        )

    # 2. Capture Table Statistics (Row Counts)
    table_stats = []
    schemas_to_monitor = ["raw", "public"]

    with engine.connect() as conn:
        for schema in schemas_to_monitor:
            # Get all tables in schema
            tables_query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = :schema
                AND table_type = 'BASE TABLE'
            """)
            tables = conn.execute(tables_query, {"schema": schema}).fetchall()

            for (table_name,) in tables:
                count_query = text(
                    f'SELECT count(*) FROM "{schema}"."{table_name}"'
                )
                row_count = conn.execute(count_query).scalar()
                table_stats.append({
                    "run_id": run_id,
                    "schema_name": schema,
                    "table_name": table_name,
                    "row_count": row_count
                })

    # 3. Persist to ops schema (Self-healing: Ensure tables exist)
    with engine.begin() as conn:
        # a) Ensure schema and tables
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ops;"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ops.pipeline_runs (
                run_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds FLOAT
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ops.dbt_results (
                id SERIAL PRIMARY KEY,
                run_id TEXT NOT NULL,
                unique_id TEXT NOT NULL,
                status TEXT NOT NULL,
                execution_time FLOAT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ops.table_stats (
                id SERIAL PRIMARY KEY,
                run_id TEXT NOT NULL,
                schema_name TEXT NOT NULL,
                table_name TEXT NOT NULL,
                row_count BIGINT,
                last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        # b) Record Pipeline Run
        conn.execute(text("""
            INSERT INTO ops.pipeline_runs (run_id, status)
            VALUES (:run_id, 'SUCCESS')
            ON CONFLICT (run_id) DO UPDATE SET status = 'SUCCESS',
            completed_at = CURRENT_TIMESTAMP;
        """), {"run_id": run_id})

        # b) Record dbt Results
        if dbt_results_data:
            conn.execute(text("""
                INSERT INTO ops.dbt_results (
                    run_id, unique_id, status, execution_time, message
                )
                VALUES (
                    :run_id, :unique_id, :status, :execution_time, :message
                )
            """), dbt_results_data)

        if table_stats:
            conn.execute(text("""
                INSERT INTO ops.table_stats (
                    run_id, schema_name, table_name, row_count
                )
                VALUES (:run_id, :schema_name, :table_name, :row_count)
            """), table_stats)

    # 4. Add Metadata to Asset (to see it in Dagster UI)
    context.add_output_metadata({
        "dbt_models_checked": len(dbt_results_data),
        "tables_monitored": len(table_stats),
        "total_rows_ingested": sum(
            s["row_count"] for s in table_stats if s["schema_name"] == "raw"
        )
    })

    return "Operational metrics successfully refreshed."
