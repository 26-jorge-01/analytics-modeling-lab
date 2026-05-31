# Changelog

All notable changes to the Analytics Modeling Lab / SECOP Intelligence project.

---

## [Unreleased] — Resilience Hardening & Referential Integrity

### Fixed

- **`stg_secop__contracts_api` — NaN timestamp crash**: Wrapped all `cast(... as timestamp)` calls with `nullif(cast(... as text), 'NaN')`. Raw JSON-API data frequently contains the literal string `'NaN'` in date columns (instead of NULL), which caused `invalid input syntax for type timestamp` errors on ~5–10% of records. ([`stg_secop__contracts_api.sql`](transform/dbt/models/staging/stg_secop__contracts_api.sql))

- **`int_secop__contracts_audit` — text subtraction error**: Changed the source from `source('raw', 'secop_contracts')` to `ref('stg_secop__contracts_api')`. The raw source stores `valor_del_contrato` as text; the staging model properly casts it to `decimal(38, 4)`. Without this fix, `ABS(valor_del_contrato - prev_value)` raised `operator does not exist: text - text`. ([`int_secop__contracts_audit.sql`](transform/dbt/models/intermediate/core/contracts/int_secop__contracts_audit.sql))

- **`int_secop__agencies_linkage` — missing downstream columns**: Added `compared_against_anchor`, `compared_against_name`, `algorithm_confidence`, and `linkage_tier` to the linkage output. Audit models (`audit_secop__agency_gray_areas`, `audit_secop__agency_matches`) depended on these columns but they were not emitted by the linkage CTE. ([`int_secop__agencies_linkage.sql`](transform/dbt/models/intermediate/core/agencies/int_secop__agencies_linkage.sql))

- **`dim_secop__agencies` — QUALIFY syntax error on PostgreSQL**: Replaced Snowflake-only `QUALIFY` clause with a standard `row_number()` subquery + `WHERE rn = 1`. PostgreSQL does not support `QUALIFY`. ([`dim_secop__agencies.sql`](transform/dbt/models/marts/core/dim_secop__agencies.sql))

- **`int_secop__contracts` — 5.6M FK violations from mismatched agency_key**: Previously generated `agency_key = md5(nit_entidad)` while `int_secop__agencies` used `md5(canonical_nit, subdivision_type, departamento)` — two completely incompatible surrogate key algorithms. Rewrote to LEFT JOIN with the golden agencies table on `(nit_entidad, departamento)` and pick the resolved `agency_key`, restoring referential integrity. ([`int_secop__contracts.sql`](transform/dbt/models/intermediate/core/int_secop__contracts.sql))

### Changed

- **`core.yml` — location_key not_null → warn**: Downgraded `location_key` not_null test from error to warning. ~113k contracts (2% of 5.6M) lack both `departamento` and `municipio_de_obtencion` in the source data — a legitimate business anomaly that should not block the pipeline. ([`core.yml`](transform/dbt/models/intermediate/core/core.yml))

- **`stg_secop__contracts_api` — incremental materialization**: Switched from `materialized='table'` to `materialized='incremental'` with a 3-day lookback window, reducing full-refresh overhead during development. ([`stg_secop__contracts_api.sql`](transform/dbt/models/staging/stg_secop__contracts_api.sql))
