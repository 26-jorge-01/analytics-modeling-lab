# 🌌 Galaxy Schema — Cross-Process Fact Constellation

> **Layer role:** Enables correlation analysis across independent business processes by sharing conformed dimensions between multiple fact tables.

---

## Models

| Model | Processes Connected | Business Question |
| :--- | :--- | :--- |
| `fct_order_experience` | Order Logistics + Customer Reviews | Does delivery performance cause sentiment change? |

---

## Architectural Pattern: Fact Constellation

A Galaxy Schema (Fact Constellation) extends the Star Schema by allowing multiple fact tables to share the same dimension tables. The enabling condition is **dimension conformity** — shared dimensions must have the same grain and the same key definition across facts.

```
dim_customer ──┬── fct_order_item    (Star Schema: Revenue analysis)
               └── fct_order_experience  (Galaxy Schema: Experience analysis)

dim_date ──────┬── fct_order_item
               └── fct_order_experience
```

Because `dim_customer` and `dim_date` are conformed across both facts, an analyst can ask: "Which customers spent over R$500 AND gave us a 1-star review in the same month?" — a query that crosses two independent business processes.

---

## Why This Matters Beyond Silos

Traditional BI implementations separate Logistics, Sales, and CX into independent star schemas owned by different teams. This creates **analytical silos**: teams can answer questions within their domain, but causality across domains remains invisible.

The `fct_order_experience` model explicitly surfaces a causal hypothesis:

```
delivery_delay_days  →  review_score  →  is_negative_review
```

This is not a reporting model. It is a **hypothesis vehicle** — a model designed to answer "Does the data support this business hypothesis?" with a single GROUP BY query.

---

## The Conformed Dimension Contract

The Galaxy Schema only works if `order_id` in `fct_order_experience` maps to the same entity as `order_id` in `fct_order_item`. This is guaranteed by both facts sourcing from `core_orders` — a single integrated entity from the Core 3NF layer.

Breaking this contract (sourcing from different upstream tables) would produce a **spurious join** — one of the most dangerous and hard-to-detect data quality failures in a warehouse.

---

## References

- [Marts Overview](../README.md) — Multi-paradigm strategy
- [Star Schema](../star/README.md) — Foundational facts that share dimensions
- [AI Readiness](../ai_readiness/README.md) — Next-level analysis using experience signals as features
