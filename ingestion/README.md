# 📥 Ingestion Layer — Extract & Load

> **Layer role:** Bronze entry point. Responsible for landing raw data into the warehouse with guaranteed schema contracts and idempotent behavior.

---

## Design Decision: Custom Python over Managed Connectors

The ingestion is implemented as a **custom Python EL script** (`extract_load.py`) rather than a managed connector (Fivetran, Airbyte). This was an intentional architectural choice, not a constraint:

| Factor | Managed Connector | Custom Python (chosen) |
| :--- | :--- | :--- |
| **Setup time** | Minutes | Hours |
| **Flexibility** | Convention-bound | Full control over pre-landing logic |
| **Cost at scale** | License per connector | Compute cost only |
| **Pre-clean logic** | Limited / post-load | Applied at read time (e.g., encoding fixes) |
| **Auditability** | Black-box transforms | Fully version-controlled logic |

For a research lab demonstrating architectural mastery, the ability to show controlled, explicit loading behavior outweighs the convenience of a managed tool.

---

## Idempotency Strategy

The script is designed to be **safely re-runnable**. Re-executing the ingestion does not create duplicate records:

```python
# Strategy: TRUNCATE + INSERT (not APPEND)
# Each run delivers a complete, fresh snapshot of the source data
# into the raw schema — consistent with a "full-load" CDC pattern.
```

**Trade-off acknowledged:** Full-load idempotency is acceptable for this dataset (static CSVs). For a production streaming source, this layer would be replaced with an incremental watermark strategy, and the Data Vault layer (which is insert-only) would absorb the change detection responsibility.

---

## Schema Governance

Each CSV source is loaded into a dedicated table in the `raw` schema, with explicit column type definitions. This enforces a **data contract at the boundary**:

- Strings are not silently coerced
- Nulls are preserved (not defaulted)
- Row counts per file are logged for observability

Downstream Soda quality scans then validate these contracts before any transformation begins.

---

## References

- [Staging Layer](../transform/dbt/models/staging/README.md) — Next layer in the pipeline
- [Ops/Infrastructure](../ops/README.md) — Database initialization and schema setup
