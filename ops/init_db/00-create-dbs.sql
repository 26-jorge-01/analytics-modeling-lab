-- Create databases idempotently (safe to run even if they already exist)
SELECT 'CREATE DATABASE dagster_meta OWNER demo'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dagster_meta')\gexec

SELECT 'CREATE DATABASE metabase_db OWNER demo'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'metabase_db')\gexec

\connect modeling_lab;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;