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

---

## 🚀 2026 Update: SECOP II (Unified Matrix)

The staging layer has been enhanced to support the **SECOP II (Colombian Public Procurement)** dataset using a "Unified Matrix" approach.

### Key Strategy: Zero-Loss Preservation
We use the `dbt_utils.star` pattern in `stg_secop__contracts_api.sql` to explicitly curate and audit critical business columns while automatically preserving 100+ raw attributes.

### Data Vault (DV) Stabilization
- **Preserved Casing**: Categorical fields avoid normalization (lower/trim) at this layer to ensure high-fidelity historical records in the Data Vault.
- **High-Precision**: All currency and value fields are cast to `DECIMAL(20, 4)` to maintain BI-grade accuracy across the Medallion lifecycle.
- **Robust Watermarking**: Implemented a multi-level fallback for `fecha_referencia` (`Signature` -> `Start` -> `Update Watermark`) to ensure 100% data freshness integrity.

---

## References

- [Ingestion Layer](../../../ingestion/README.md) — Upstream data source
- [Core 3NF](./../../intermediate/core/README.md) — Downstream integration layer
- [Data Vault](./../../intermediate/vault/README.md) — Downstream history layer
