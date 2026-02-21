# 🧪 Analytics Modeling Lab
## *Evaluating Data Modeling Paradigms in the Modern Data Stack*

[![Environment](https://img.shields.io/badge/Infrastructure-Docker-blue.svg)]()
[![Orchestration](https://img.shields.io/badge/Orchestration-Dagster-red.svg)]()
[![Transformation](https://img.shields.io/badge/Transformation-dbt-orange.svg)]()
[![Modeling](https://img.shields.io/badge/Paradigm-3NF_|_Data_Vault_|_Star-green.svg)]()

### 🎯 The Mission
This project is an **Engineering Research Laboratory** designed to evaluate how different data modeling strategies impact downstream analytical performance, auditing capabilities, and AI readiness. 

Rather than building a simple pipeline, this lab demonstrates the application of **Software Engineering principles** (Idempotency, Version Control, Automated Testing) to the Data Lifecycle. It serves as a proof-of-concept for handling complex transactional data streams across competing modeling paradigms.

---

## 🏛️ Architectural Strategy & Design Choices
I have implemented a **Modular Modern Data Stack (MDS)** to ensure strict decoupling of storage, compute, and orchestration.

```mermaid
graph TD
    subgraph Ingestion
        Raw["Raw Data (CSVs)"] --> |Python| PGL[("Postgres (Raw Layer)")]
    end
    
    subgraph "Engineering Playground (Software-Defined Assets)"
        Dagster["Dagster (Orchestrator)"]
        dbt["dbt (Modeling Engine)"]
        
        Dagster <--> |Lineage & State| dbt
        dbt --> |Star Schema| PGL
        dbt -.-> |Next Milestones| DV["Data Vault"]
    end

    subgraph "Consumer Ecosystem"
        PGL --> |Dashboarding| Metabase["Metabase"]
        PGL -.-> |Downstream| AI["AI / ML Flows"]
    end
```

### 🧠 Technical Justification

| Component | Strategic Justification | Engineering Value |
| :--- | :--- | :--- |
| **Dagster** | Chosen for its **Software-Defined Assets (SDA)** paradigm. Unlike task-based orchestrators, Dagster focuses on the *state* of data, enabling explicit lineage and granular observability. | Eliminates "black box" failures; enables asset-level recovery. |
| **dbt** | Treats SQL as a first-class engineering language. Implements modular builds and automated testing. | Ensures **DRY (Don't Repeat Yourself)** code and high data trust. |
| **Multi-Schema Postgres** | Simulates a Data Warehouse environment with isolated layers (Raw, Staging, Marts) to prevent cross-contamination. | Enforces strict data governance and security boundaries. |

---

## 🚀 Multi-Paradigm Modeling: Why it Matters
I demonstrate three distinct modeling strategies on a single e-commerce stream, each serving a unique business and technical user:

1.  **Third Normal Form (3NF)**: *The Operational Source of Truth.* Designed for data integrity and minimal storage footprint. 
    *   **Value**: Ideal for verifying raw transactional consistency.
2.  **Data Vault (v1)**: *The Enterprise Backbone.* Built for scalability and auditing. Decouples business keys (Hubs), relationships (Links), and descriptive history (Satellites).
    *   **Value**: Essential for tracking CDC (Change Data Capture) without losing historical state.
3.  **Star Schema (LIVE)**: *The Performance Layer.* Denormalized dimensions and fact tables optimized for compute speed.
    *   **Value**: Reduces join complexity for BI tools and improves query latency.

---

## 💼 Architecture as a Business Enabler
I selected a modeling paradigm not just for technical elegance, but to solve specific executive and operational needs. This lab demonstrates how architecture drives decision-making:

| Paradigm | Business Persona | Simple Business Question | Technical Why |
| :--- | :--- | :--- | :--- |
| **3NF** | **Operations** | "Is the amount paid by the customer exactly the same as the product price plus shipping?" | Ensures data integrity and catches calculation errors. |
| **Data Vault** | **Audit / History** | "Where exactly are orders getting stuck (warehouse vs. delivery) and has this improved over time?" | Tracks historical status changes without losing previous states. |
| **Star Schema** | **Management** | "Which product categories are our top sellers today and are we growing compared to last month?" | Optimized for lightning-fast sales reports and growth trends. |
| **Galaxy** | **Customer Success** | "Do customers give us lower ratings when their packages arrive later than promised?" | Connects different processes (Logistics vs. Reviews) to find patterns. |

---

## 🤖 AI & ML Readiness
This lab is architected to feed the AI Lifecycle:

*   **RAG Context**: The normalized 3NF and Staging layers provide clean, structured context for LLM retrieval.
*   **Feature Stores**: Dimension tables in the Star Schema serve as ready-to-use feature vectors for ML models.
*   **Backtesting Truth**: The Data Vault's historical satellites provide the "point-in-time" snapshots required for accurate model validation.

---

## 🛠️ Implementation & Quickstart

### Reproducible Environment
The entire stack is containerized. Environmental configurations are managed via a central `.env` file (abstracted from `docker-compose.yml`) to ensure production-like portability.

```bash
# Initialize
copy .env.example .env
.\make.bat up

# Execute Asset Lineage
.\make.bat ingest     # Extract & Load
.\make.bat dbt-build  # Multi-layer Transformation
.\make.bat dbt-serve  # Inspect Documentation & Lineage (localhost:8099)
```

---

## 📅 Roadmap to Enterprise Maturity
*   **Milestone 1: Foundational Analytics (MVP - COMPLETED)**: Reliable ingestion, staging, and Star Schema for core sales metrics.
*   **Milestone 2: Governance & History (v1)**: Implementation of Data Vault for full auditability and Soda.io for declarative data quality.
*   **Milestone 3: Advanced Intelligence (v2)**: Galaxy schemas for multi-process analysis and automated feature engineering for churn prediction.
