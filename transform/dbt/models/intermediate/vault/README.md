# 🔐 Data Vault 2.0 — The Auditable Enterprise Backbone

> **Layer role:** Insert-only historical record of all source data changes. Provides the mathematical guarantee that no business event is ever overwritten or deleted.

---

## Why Data Vault?

Data Vault is not adopted for its elegance — it is adopted because of what it makes **impossible to do wrong**:

| Failure Mode | 3NF Warehouse | Data Vault |
| :--- | :--- | :--- |
| Overwriting a customer's address | Silently done by `UPDATE` | Structurally impossible (new Sat row only) |
| Losing the status before a cancellation | Common | Preserved in Satellite history |
| Adding a new source without schema migration | Requires ALTERs | Add a new Satellite, zero impact on existing |
| Proving what the data said on a specific date | Requires audit tables | Native point-in-time query |

In a compliance-sensitive environment, these are not preferences — they are regulatory requirements. This project implements DV to demonstrate the ability to operate at that level.

---

## Component Architecture

```
Hub_Order  ──────────────────────┐
                                 │
Hub_Customer ──── Link_Order_Customer
                                 │
                         Sat_Order_Details
                         Sat_Customer_Details
```

| Component | Role | Key Characteristic |
| :--- | :--- | :--- |
| **Hub** | Identity registry for a business concept | Contains only the Business Key (BK) + metadata |
| **Link** | Relationship between two or more Hubs | The "unit of work" — no attributes |
| **Satellite** | Descriptive attributes + change history | One row per load event, never updated |

Hubs enforce business key uniqueness. Links are the only structural record of a relationship. Satellites are append-only — a `load_date` column combined with `ROW_NUMBER()` in the Core layer derives the current state.

---

## Surrogate Keys

All PKs in this layer are **deterministic MD5 hash keys** generated from the business key:

```sql
md5(cast(order_bk as text)) as order_pk
```

This ensures that the same source record always generates the same PK — enabling idempotent loads and cross-system reconciliation without a sequence generator.

---

## Point-in-Time Queries

The Data Vault enables queries that are architecturally impossible in a mutable OLTP or Star Schema warehouse:

```sql
-- "What was the order status of order X on a specific historical date?"
select order_status
from sat_order_details
where order_pk = :target_pk
  and load_date <= :target_date
order by load_date desc
limit 1;
```

This capability is what separates a data warehouse from a data archive.

---

## References

- [Staging Layer](../../staging/README.md) — Upstream raw source
- [Core 3NF](../core/README.md) — Derived integration view of Vault entities
