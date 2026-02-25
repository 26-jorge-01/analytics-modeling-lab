# 🏛️ Core 3NF — The Integrated Silver Layer

> **Layer role:** Derives clean, integrated business entities from the Data Vault. Provides a consistent operational view used as the primary source for all Gold layer models.

---

## Why 3NF Sits Above the Data Vault

A common question in modern data stacks is whether the Data Vault or 3NF serves as the "source of truth." In this architecture, the answer is **both, at different levels of abstraction:**

| Concern | Data Vault | Core 3NF |
| :--- | :--- | :--- |
| **Historical accuracy** | ✅ Full insert-only record | ❌ Point-in-time view only |
| **Join complexity** | ❌ Hub + Link + Sat per entity | ✅ Single clean table per entity |
| **Downstream usability** | ❌ Requires DV knowledge | ✅ Standard SQL patterns |
| **Referential integrity** | ❌ Structural, not enforced | ✅ Business key relationships tested |

The Core layer resolves the DV complexity into **opinionated business entities** that downstream teams can use without understanding Data Vault mechanics.

---

## Key Pattern: Latest-Satellite Derivation

Satellites store one row per change event. The Core layer always derives the **current state** using a `ROW_NUMBER() OVER (PARTITION BY pk ORDER BY load_date DESC)` pattern:

```sql
-- Standard pattern across all core models
latest_sats as (
    select *,
        row_number() over (
            partition by order_pk order by load_date desc
        ) as rn
    from sats
    where rn = 1
)
```

This pattern is consistent, testable, and avoids `MAX(load_date)` subquery anti-patterns that degrade at scale.

---

## Relational Integrity via dbt Tests

Core models enforce integrity that the Data Vault layer intentionally does not:

- `relationships` tests validate that every `customer_id` in `core_orders` exists in `core_customers`
- `not_null` tests on business keys catch upstream loading failures early
- These tests run on every `dbt build`, not just during development — they are **production gates**

---

## References

- [Data Vault](../vault/README.md) — Upstream source of Core entities
- [Marts Overview](../../marts/README.md) — Downstream consumers
- [Star Schema](../../marts/star/README.md) — Primary Gold consumer of Core models
