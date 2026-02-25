# 🎯 Marts — The Gold Layer

> **Layer role:** Consumption-optimized analytical models. Each mart paradigm is a deliberate architectural choice targeting a specific query profile, team, and update pattern.

---

## Navigation

| Paradigm | Path | Query Profile |
| :--- | :--- | :--- |
| **⭐ Star Schema** | [star/README.md](./star/README.md) | High-volume BI queries, low join depth |
| **❄️ Snowflake Model** | [snowflake/README.md](./snowflake/README.md) | Hierarchical management, atomic attribute updates |
| **🌌 Galaxy Schema** | [galaxy/README.md](./galaxy/README.md) | Cross-process correlation, conformed dimensions |
| **🤖 AI Readiness** | [ai_readiness/README.md](./ai_readiness/README.md) | Feature vectors for ML training and inference |

---

## The Multi-Paradigm Decision

A single modeling paradigm cannot optimally serve all analytical consumers. The decision to implement four parallel paradigms is driven by a fundamental engineering insight:

> *The "best" data model is defined by its consumer's query pattern — not by an abstract standard.*

| Consumer | Query Pattern | Bottleneck | Optimal Paradigm |
| :--- | :--- | :--- | :--- |
| Metabase BI Analyst | Aggregating metrics over time | Join depth | Star Schema |
| Territory Manager | Looking up a single region's attributes | Write amplification on updates | Snowflake Model |
| Customer Success Team | Correlating two business processes | Cross-fact joins | Galaxy Schema |
| Data Scientist | Retrieving feature vectors for a cohort | Feature freshness, batch extraction | AI Readiness |

Building all four in the same project — from the same upstream Core layer — demonstrates the ability to reason about this decision explicitly and implement it systematically.

---

## Shared Foundation: Conformed Dimensions

All paradigms in this layer draw from the same Core 3NF models. Customer IDs, Product IDs, and Date keys are **conformed** — their grain and identity are consistent across all facts. This is what makes the Galaxy Schema possible: you can join facts from different paradigms because their shared dimension keys are identical.

---

## Upstream Reference

- [Core 3NF](../intermediate/core/README.md) — Source of all mart models
- [dbt Project](../../../README.md) — Transformation project overview
