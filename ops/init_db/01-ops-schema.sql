-- Creation of the operational schema for monitoring and metrics
CREATE SCHEMA IF NOT EXISTS ops;

-- Tracking high-level pipeline runs
CREATE TABLE IF NOT EXISTS ops.pipeline_runs (
    run_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds FLOAT
);

-- Tracking individual dbt model/test results
CREATE TABLE IF NOT EXISTS ops.dbt_results (
    id SERIAL PRIMARY KEY,
    run_id TEXT NOT NULL,
    unique_id TEXT NOT NULL,
    status TEXT NOT NULL,
    execution_time FLOAT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracking table-level statistics (Data Governance)
CREATE TABLE IF NOT EXISTS ops.table_stats (
    id SERIAL PRIMARY KEY,
    run_id TEXT NOT NULL,
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    row_count BIGINT,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
