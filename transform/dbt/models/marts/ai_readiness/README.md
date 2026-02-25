# 🤖 AI Readiness — The Intelligence Layer

> **Layer role:** Produces feature-engineered analytical datasets purpose-built for machine learning workflows. Eliminates the data preparation overhead that consumes 80% of a data scientist's time.

---

## Models

| Model | ML Problem | Feature Type |
| :--- | :--- | :--- |
| `fct_customer_churn_features` | Binary churn classification | RFM (Recency, Frequency, Monetary) |

---

## The Feature Engineering Problem

The most common friction point between Data Engineering and Data Science is **feature availability**. A data scientist building a churn model needs:

1. A stable, versioned extract of customer attributes at a specific point in time
2. Derived behavioral signals (recency, frequency, monetary value) — not raw transactions
3. A binary label (`is_churned_candidate`) based on a business-defined threshold
4. The same data pipeline running in production inference, not just training

Without an AI Readiness layer, the data scientist either:
- Writes their own SQL against raw tables (bypassing all quality gates)
- Depends on a data engineering ticket for each feature request

`fct_customer_churn_features` eliminates both failure modes by making features a **first-class warehouse artifact** — tested, documented, and governed the same way as any business metric.

---

## RFM Signals Produced

```sql
total_orders         -- Frequency
total_spent          -- Monetary
days_since_last_order -- Recency (derived from current_date - max order date)
avg_order_value      -- Derived monetary signal
is_churned_candidate -- Label: TRUE if days_since_last_order > 90
```

The 90-day threshold for churn is configurable. In a production context, this would be externalized as a dbt variable (`{{ var('churn_threshold', 90) }}`), allowing the model to be re-run with different business definitions without code changes.

---

## Production Considerations

This layer is the boundary between **Data Engineering** and **ML Platform engineering**. In production:

- These features would be materialized to a **Feature Store** (Vertex AI, SageMaker Feature Group) via a downstream export job
- The Data Vault's point-in-time query capability would enable **training set construction** for any historical period, preventing data leakage
- `is_churned_candidate` is a label, not a prediction — the ML model produces the probability score

The architecture is designed to grow into that production pattern without structural change.

---

## References

- [Marts Overview](../README.md) — Multi-paradigm context
- [Galaxy Schema](../galaxy/README.md) — `fct_order_experience` provides additional behavioral signals for enriched feature sets
- [Data Vault](../../intermediate/vault/README.md) — Source of historical point-in-time data for ML backtesting
