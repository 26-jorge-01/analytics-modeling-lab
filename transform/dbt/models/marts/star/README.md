# ⭐ Star Schema — The BI Performance Layer

> **Layer role:** Denormalized analytical views optimized for BI tool query patterns. Trades storage efficiency for query speed and join simplicity.

---

## Models

| Model | Grain | Type |
| :--- | :--- | :--- |
| `fct_order_item` | One row per order line item | Fact |
| `dim_customer` | One row per unique customer | Dimension |
| `dim_product` | One row per product SKU | Dimension |
| `dim_date` | One row per calendar date | Dimension |

---

## The Denormalization Decision

Star Schema deliberately violates 3NF by embedding attributes that could be normalized into the dimension tables. For example, `dim_customer` includes `city` and `state` even though these are hierarchical (city belongs to state). The rationale:

**The cost of a join in a BI query is not just computational — it is cognitive.**

A Metabase analyst writing `SELECT ... FROM fct_order_item JOIN dim_customer` should not have to navigate a three-table geography hierarchy to get a customer's region. Every additional join is a potential mistake, a performance penalty, and a barrier to self-service analytics.

The trade-off: an `UPDATE` to a customer's city would require updating every row in `dim_customer` where that city appears. At the scale of this dataset, that is acceptable. At petabyte scale, this is where the Snowflake Model becomes the correct answer.

---

## Schema Tests as Production Gates

The `schema.yml` in this directory defines tests that run on every `dbt build`:

- `unique` + `not_null` on all primary keys
- `relationships` validates that every `customer_id` in `fct_order_item` exists in `dim_customer`
- `accepted_values` on `order_status` prevents unknown enum values from reaching dashboards

These tests are not "nice to have." They are the gate between transformation and consumption. A model that passes its tests is a model that can be trusted in production.

---

## References

- [Marts Overview](../README.md) — Multi-paradigm context
- [Core 3NF](../../intermediate/core/README.md) — Upstream source models
- [Snowflake Model](../snowflake/README.md) — When star schema denormalization breaks down
