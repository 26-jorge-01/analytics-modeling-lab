# ⚙️ Ops — Infrastructure & Developer Experience

> **Layer role:** Infrastructure definition, database initialization, linting configuration, and developer tooling. Everything required to go from a fresh clone to a running pipeline in under 5 minutes.

---

## Navigation

| Area | File | Purpose |
| :--- | :--- | :--- |
| **Container stack** | `docker-compose.yml` | Multi-service orchestration |
| **DB initialization** | `init_db/00-create-dbs.sql` | Idempotent database setup |
| **SQL linting** | `.sqlfluff` | Enforced SQL style rules |
| **Python linting** | `.flake8` | Enforced Python style rules |
| **Developer CLI** | `make.bat` | Unified command interface |

---

## Idempotent Database Initialization

The `00-create-dbs.sql` init script uses a conditional creation pattern to prevent failures on existing volumes:

```sql
SELECT 'CREATE DATABASE metabase_db OWNER demo'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'metabase_db')\gexec
```

**Why this matters:** Docker's init scripts only execute on a fresh volume. In practice, developers rebuild their images frequently but preserve their data volumes. Without this pattern, a `docker compose up` after an image rebuild (but not a volume reset) would fail silently on database creation, causing downstream service failures.

The `\gexec` metacommand executes the result of the `SELECT` as SQL — a standard PostgreSQL pattern for conditional DDL.

---

## Multi-Database Architecture

Three databases coexist in a single Postgres instance:

| Database | Owner | Purpose |
| :--- | :--- | :--- |
| `modeling_lab` | `demo` | Primary warehouse (raw + staging + marts) |
| `dagster_meta` | `demo` | Dagster run history and asset materialization state |
| `metabase_db` | `demo` | Metabase application state (dashboards, users, questions) |

Separating Metabase's application database from the warehouse is not optional — the default Metabase H2 file-based engine loses all dashboards on container restart. PostgreSQL-backed persistence is the correct production configuration.

---

## Linting as a Quality Gate

SQLFluff and Flake8 run as CI/CD gates before any code is merged:

```bash
# CI pipeline steps
sqlfluff lint transform/dbt/models --dialect postgres  # SQL style enforcement
flake8 ingestion/ orchestration/                       # Python style enforcement
```

The `.sqlfluff` configuration enforces:
- Explicit `AS` keywords on all table aliases (`AL01`)
- `SELECT *` only at the CTE terminal select, not in subqueries
- Trailing comma style consistency

Style rules are not enforced because they are "nice to have" — they are enforced because inconsistent code increases cognitive load during code review and is a leading indicator of logic errors.

---

## Developer CLI (`make.bat`)

The `make.bat` file provides a single-command interface for all pipeline operations:

```bash
.\make.bat up          # Start full stack
.\make.bat down        # Stop all containers
.\make.bat ingest      # Run CSV → Raw ingestion
.\make.bat dbt-build   # Run all dbt transformations
.\make.bat dbt-serve   # Serve dbt docs + lineage (localhost:8099)
.\make.bat dq          # Run Soda quality scans
.\make.bat lint        # Run sqlfluff + flake8
```

The goal is **zero-documentation onboarding**: a new developer should be able to run the full pipeline on their first day without reading anything other than this file.

---

## References

- [Main Architecture](../README.md) — System overview
- [Dagster Orchestration](../orchestration/dagster/README.md) — Services managed by Docker
