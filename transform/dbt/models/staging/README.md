# 🥉 Staging Layer — Bronze Foundation

> **Layer role:** Source system decoupling. Staging mirrors raw sources with minimal transformation, enforcing typed interfaces that protect every downstream layer from source schema changes.

---

## Architecture Principle: 1-to-1 Source Reflection

Each staging model corresponds to exactly one source table. **No joins occur at this layer.** This is a strict architectural constraint, not a preference:

- Joining at staging couples two source schemas, amplifying the blast radius of any upstream change
- Staging models are views by default — they add no storage cost while providing a stable interface
- The `src_olist.yml` source definition acts as the contract: freshness thresholds, source-level tests, and column documentation are co-located here

If a source column is renamed, **only the staging model changes** — every downstream model continues to reference the stable staging alias.

---

## Transformations Applied

Staging applies exactly three classes of transformation, nothing more:

| Class | Example | Rationale |
| :--- | :--- | :--- |
| **Type casting** | `::timestamp`, `::numeric` | Ensures predictable types before any logic runs |
| **Column aliasing** | `customer_zip_code_prefix → zip_code_prefix` | Standardizes naming convention across sources |
| **Structural cleanup** | Selecting only needed columns | Reduces compute in downstream materializations |

Business logic (joining, aggregating, deriving KPIs) begins at the **Intermediate layer**.

---

## Source Contract: `src_olist.yml`

The source YAML file defines:
- **Data freshness thresholds** — Soda alerts if raw data hasn't been refreshed within the configured window
- **Column-level tests** — `not_null`, `unique` on primary keys validated directly at the source
- **Documentation** — Column descriptions propagate through the dbt DAG into the served documentation site

This ensures that quality failures are caught at the earliest possible point in the lineage, rather than surfacing as corrupted Mart data.

---

## References

- [Ingestion Layer](../../../ingestion/README.md) — Upstream data source
- [Core 3NF](./../../intermediate/core/README.md) — Downstream integration layer
- [Data Vault](./../../intermediate/vault/README.md) — Downstream history layer
