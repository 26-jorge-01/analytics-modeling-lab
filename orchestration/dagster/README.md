# 🎻 Dagster Orchestration — Asset-Based Data Orchestration

> **Layer role:** Defines, schedules, and monitors the full data pipeline as a graph of software-defined assets. Provides lineage, observability, and re-materialization control at the asset level.

---

## Navigation

| Section | Topic |
| :--- | :--- |
| [Architecture Decision](#architecture-decision-assets-vs-tasks) | Why Dagster over Airflow |
| [Asset Graph Structure](#asset-graph-structure) | How the pipeline is modeled |
| [Reliability Pattern](#reliability-pattern-circuit-breaker) | Quality gates in the DAG |

---

## Architecture Decision: Assets vs. Tasks

Dagster's asset-based model is a fundamentally different paradigm from task-based orchestrators (Airflow, Prefect):

| Dimension | Task-Based (Airflow) | Asset-Based (Dagster) |
| :--- | :--- | :--- |
| **Mental model** | "Run this function" | "Produce this dataset" |
| **Lineage visibility** | Implicit in DAG edges | First-class: assets know their upstream dependencies |
| **Re-run granularity** | Entire DAG or task group | Individual asset or any subgraph |
| **Failure recovery** | Manual retry from checkpoint | Auto-detect stale assets; re-materialize only what changed |
| **Testing** | Mock DAG execution | `build_asset_context()` for unit-testable asset functions |

For a data engineering portfolio, Dagster's explicit lineage model makes the pipeline's intent visible without reading code — a meaningful difference when being evaluated by a technical reviewer.

---

## Asset Graph Structure

```
raw_quality_check          (Soda: validates raw schema)
       │
       ▼
staging_models             (dbt: stg_*)
       │
       ▼
intermediate_models        (dbt: hub_*, link_*, sat_*, core_*)
       │
       ▼
mart_models                (dbt: Star + Snowflake + Galaxy + AI)
       │
       ▼
gold_quality_check         (Soda: validates mart outputs)
```

The Soda quality checks are modeled as assets with explicit dependencies — not as post-hooks or side effects. This ensures that if a Soda check fails, Dagster correctly marks all downstream assets as stale and prevents their execution.

---

## Reliability Pattern: Circuit Breaker

The `raw_quality_check` asset implements the circuit breaker pattern: before any dbt model runs, Soda validates the raw schema for completeness, freshness, and null rates. If the check fails, the pipeline stops — poison data cannot propagate to analytical layers.

This is the equivalent of a schema registry validation in a Kafka ecosystem: you do not allow bad records to enter the stream.

---

## Structural Requirements: Package Initialization

Inside the `dagster_project/assets` directory, a strict package structure must be maintained to ensure the code loader can resolve relative imports correctly, especially when running in Docker or as an editable package.

> [!IMPORTANT]
> Every nested subdirectory (e.g., `bronze/`, `silver/`, `gold/`) **must** contain an `__init__.py` file. Failure to include these will result in a `DagsterCodeLocationLoadError` (ImportError), as Dagster’s internal module discovery requires explicit package boundaries for nested asset modules.

---

## References

- [Main Architecture](../../README.md) — System-level orchestration flow
- [Quality Gates](../../quality/README.md) — Soda check details
- [dbt Project](../../transform/dbt/README.md) — Models triggered by Dagster assets
