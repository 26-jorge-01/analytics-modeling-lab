# 🏗️ dbt Transformation Project — The Modeling Engine

> **Project scope:** All SQL transformation logic from raw source data to multi-paradigm analytical models. Covers 28+ models across 4 architectural layers.

---

## Navigation

| Layer | Path | Role |
| :--- | :--- | :--- |
| **Staging** | [`models/staging/`](./models/staging/README.md) | Source decoupling, type casting |
| **Data Vault** | [`models/intermediate/vault/`](./models/intermediate/vault/README.md) | Insert-only history |
| **Core 3NF** | [`models/intermediate/core/`](./models/intermediate/core/README.md) | Integrated operational view |
| **Marts** | [`models/marts/`](./models/marts/README.md) | Consumption-optimized paradigms |

---

## Project Design Philosophy

### Why dbt?
dbt transforms SQL from a scripting language into a **software engineering practice**. The non-negotiables in this project:

- **Modularity**: Every model is a composable unit. `fct_order_item` references `core_orders` via `ref()` — not a hardcoded schema string. Renaming a table requires changing exactly one file.
- **Testability**: `schema.yml` tests run on every build. A model that passes but produces wrong data is worse than a model that fails loudly — dbt enforces the latter.
- **Documentation as code**: Descriptions in `schema.yml` propagate into the served documentation site. Documentation that lives outside the code gets out of sync; this doesn't.
- **Deterministic builds**: `dbt build` is idempotent. Running it twice produces the same result. This is the baseline for any serious data engineering practice.

---

## Materialization Strategy

| Layer | Materialization | Rationale |
| :--- | :--- | :--- |
| **Staging** | `view` | No storage cost; always reflects current raw data |
| **Intermediate (Vault)** | `table` | Expensive joins on Hubs/Links/Sats benefit from materialization |
| **Intermediate (Core)** | `view` | Lightweight derivation; freshness inherited from Vault tables |
| **Marts** | `table` | High-concurrency BI queries require pre-materialized data |

The choice is not aesthetic — it is driven by **the cost model of repeated query execution vs. storage cost of materialized output**.

---

## Surrogate Key Standard

All surrogate keys use `dbt_utils.generate_surrogate_key()`, which produces deterministic MD5 hashes:

```sql
{{ dbt_utils.generate_surrogate_key(['order_id', 'order_item_id']) }} as order_item_key
```

This ensures cross-run consistency and enables safe incremental loading patterns in future iterations.

---

## Deprecation Management

This project targets dbt 1.11. The `schema.yml` test format has been updated to the modern `arguments` nesting syntax to eliminate deprecation warnings on generic tests (`accepted_values`, `relationships`). CI/CD runs `dbt parse` to catch schema regressions before any model runs.

---

## References

- [Main Architecture](../../../README.md) — System overview and documentation index
- [Marts Overview](./models/marts/README.md) — Gold layer paradigm guide
