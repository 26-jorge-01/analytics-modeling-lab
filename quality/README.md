# 🔍 Quality Layer — Declarative Data Quality Gates

> **Layer role:** Implements automated data quality constraints as pipeline gates, not as post-hoc reporting. Uses Soda.io's declarative YAML syntax to define, execute, and alert on data health.

---

## Architecture Pattern: Quality as a Circuit Breaker

The most common approach to data quality in a pipeline is **reactive monitoring** — dashboards that show you data is bad after it has already reached consumers. This architecture uses a **proactive circuit breaker** pattern instead:

```
Raw Data Loaded → Soda Scan (Bronze Gate) → [FAIL: stop] → Transformations
                                                         → [PASS: proceed]

dbt Build Completes → Soda Scan (Gold Gate) → [FAIL: alert] → BI consumers
                                                            → [PASS: serve]
```

If the Bronze gate fails, dbt never runs. If the Gold gate fails, Metabase receives stale-but-valid data rather than corrupted-and-new data. This is the correct failure mode.

---

## Check Design Principles

Soda checks are organized by purpose, not by table:

| Check Class | Example | Purpose |
| :--- | :--- | :--- |
| **Completeness** | `missing_count(order_id) = 0` | Catch partial loads before they propagate |
| **Freshness** | `row_count > 0` on raw tables | Detect ingestion failures early |
| **Referential** | `invalid_count(customer_id) = 0` | Catch orphaned foreign keys at the source |
| **Domain** | `invalid_percent(review_score) < 1%` | Catch schema drift / upstream enum changes |
| **Statistical** | `avg(price) between 10 and 1000` | Detect sudden distribution shifts |

Statistical checks (averages, percentiles) are particularly valuable at the Gold layer — a sudden change in average order value is either a business event or a data bug, and either way it requires immediate attention.

---

## Why Soda over dbt Tests?

dbt tests and Soda checks are complementary, not redundant:

| Capability | dbt Tests | Soda Checks |
| :--- | :--- | :--- |
| **Runs at** | Model build time | Any pipeline stage, including raw |
| **Can check raw tables** | ❌ Only dbt models | ✅ Any SQL table |
| **Business threshold checks** | Limited | ✅ First-class `warn` and `fail` thresholds |
| **Cloud alerting integration** | Via hooks | ✅ Native Soda Cloud integration |
| **Statistical checks** | ❌ | ✅ Distribution, percentile, stddev |

dbt tests enforce **structural contracts** (PKs, FKs, accepted values). Soda checks enforce **behavioral contracts** (freshness, distribution, business rules). Both are necessary.

---

## References

- [Main Architecture](../README.md) — Where quality gates sit in the system flow
- [Dagster Orchestration](../orchestration/dagster/README.md) — How Soda is triggered as assets
