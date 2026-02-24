# 🏗️ Analytics Modeling Lab: Strategic Roadmap

This document outlines the architectural evolution of the lab, moving from basic transformation to enterprise-grade governance and AI-ready data products.

---

## 🗺️ Milestone Overview

| Milestone | Objective | Key Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **M1: Foundation** | "Zero to Lab": Raw → Staging → Star Schema MVP. | Dockerized Infra, dbt Staging, Star MVP, Metabase Dashboard. | ✅ Completed |
| **M2: Governance** | Enterprise History & Quality: 3NF + Data Vault + Soda DQ. | ERD 3NF, DV Hubs/Links/Sats, Soda Health Reports, CI Pipeline. | ✅ Completed |
| **M3: Intelligence** | Advanced Modeling & AI Readiness: Snowflake/Galaxy + ML Features. | Fact Constellation, Feature Store Layer, Observability Metrics. | 📥 Backlog |

---

### Milestone 1: Foundational Analytics (MVP)
**Strategic Business Focus**: "Which product categories are our top sellers today and are we growing compared to last month?"

**Objective**: Establishing a reproducible Modern Data Stack (MDS) environment and implementing the primary consumption layer for high-velocity decision-making.

### Engineering Checklist
- [x] **Environment**: Multi-container Docker setup (Postgres, Dagster, Metabase).
- [x] **Orchestration**: Software-Defined Assets (SDA) in Dagster for `raw_load` → `dbt_build`.
- [x] **Ingestion**: Automated extraction of transactional Olist data and synthetic subscription generation.
- [x] **Transformation**: 
    - [x] Staging layer (cleaning/typing).
    - [x] Dimensional modeling (dim_customer, dim_product, fct_order_item).
- [x] **Documentation**: Automatic schema generation and lineage via dbt docs.
- [x] **BI**: Star Schema integration with Metabase for AOV and sales velocity analysis.

---

## 🏗️ Milestone 2: Enterprise Governance & History (v1)
**Strategic Business Focus**: "Is the amount paid correct, and where exactly do orders get stuck during delivery?"

**Focus**: Demonstrating auditability, historical tracking, and automated data quality.

### Architecture Goals
- **Third Normal Form (3NF)**:
    - [x] Implement `models/intermediate/core/` to provide an operational source of truth.
    - [x] Validate referential integrity via dbt tests.
- **Data Vault 2.0**:
    - [x] Implement Hubs, Links, and Satellites in `models/intermediate/vault/` to enable non-destructive historical tracking.
    - [x] Demonstrate point-in-time snapshots for auditing.
- **Automated Observability**:
    - [x] Integrate **Soda.io** for declarative data health checks (Freshness, Nullability, Schema Drift).
    - [x] Implement GitHub Actions for CI (Linting + Testing).

### Evidences (screenshots) - Borrar al terminar

- [x] ERD 3NF
- [x] DV diagram
- [x] dbt docs lineage con 3 ramas (3NF/DV/marts)
- [x] reporte de Soda
- [x] GitHub Actions green

### DoD (v1) - Borrar al terminar
- [x] make test corre: lint + unit + dbt build + soda scan
- [x] Documentación lista (diagramas + decisiones).
- [x] Lineage visible y entendible.
- [x] CI/CD Workflow structural (parse/compile/dry-run).

---

## 📥 Milestone 3: Advanced Intelligence & Scaling (v2)
**Strategic Business Focus**: "Do late deliveries lead to lower customer ratings?"

**Focus**: Complex analytical patterns and feeding the AI/ML lifecycle.

### High-Level Initiatives
- **Fact Constellation (Galaxy Schema)**:
    - [ ] Cross-process analysis (Sales vs. Returns vs. Shipments) using conformed dimensions.
- **Predictive Readiness**:
    - [ ] Create a "Feature Store" layer optimized for Churn and LTV (Life-Time Value) models.
- **Scaling Performance**:
    - [ ] Transition facts to incremental materialization strategies.
    - [ ] Implement automated performance monitoring for dbt runs.

### Evidences (screenshots) - Borrar al terminar

- [] Galaxy diagram + lineage dbt con múltiples facts.
- [] 3 dashboards con preguntas “tipo de análisis”, no “negocio”.

### DoD (v2) - Borrar al terminar
- [] make run (job completo) genera métricas + posible alerta.
- [] Galaxy diagram + lineage dbt con múltiples facts.
- [] 3 dashboards con preguntas “tipo de análisis”, no “negocio”.

---

## 🏛️ Engineering Principles Applied
*   **Idempotency**: Every asset can be re-run without side effects.
*   **Separation of Concerns**: Decoupling ingestion (Python), transformation (dbt), and orchestration (Dagster).
*   **Observability**: Data quality is treated as a first-class citizen via testing and Soda.
*   **AI-First Design**: Cleaning and modeling data specifically to serve as high-quality context for downstream AI agents and ML models.