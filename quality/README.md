# ✅ Quality Gates: Soda.io Observability

## 📖 How it Works
We use **Soda.io** to implement **Data Quality Checks**. These are declarative YAML files (`checks.yml`) that define "Healthy Data".
- **Numeric Checks**: "Price must be greater than zero".
- **Uniqueness**: "There should be 0 duplicate Order IDs".
- **Schema Checks**: "Columns must not change names without notice".

## 🚀 Why it is Important (Industry)
- **Trust**: Business stakeholders only use dashboards if they trust the data.
- **Circuit Breakers**: If the data in `raw` is garbage, Soda stops the pipeline **before** it reaches the client-facing dashboards.
- **Governance**: Automates the Boring work of data validation.

## 🧪 Use Case in this Lab
We run Soda checks immediately after both Ingestion and Transformation. This ensures that the Olist data, which can have inconsistencies, is validated against our business rules before it hits the Gold layer.

## 💡 Pro Tip for Beginners
Data Quality is not a "Nice to have"; it is a functional requirement. If you aren't testing your data, you aren't doing data engineering.
