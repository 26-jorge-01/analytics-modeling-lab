# 🎬 Orchestration: The Pipeline Conductor

## 📖 How it Works (Dagster)
We use **Dagster** as our orchestration engine. Unlike older tools (like Airflow), Dagster is **Asset-Based**.
- **Software-Defined Assets**: We don't define "Tasks"; we define "Data Products" (like `stg_orders` or `fct_sales`).
- **Lineage**: Dagster automatically understands that `fct_sales` depends on `stg_orders` and ensures they run in the correct order.

## 🚀 Why it is Important (Industry)
- **Developer Experience**: Local testing of pipelines is 10x faster and more reliable.
- **Integrations**: Seamless connections with dbt, Soda, and custom Python scripts.
- **Observability**: One unified dashboard to see the health of the entire data ecosystem.

## 🧪 Use Case in this Lab
We use the `CustomDagsterDbtTranslator` to map dbt models directly into Dagster assets. This allows us to trigger dbt runs from a professional UI and see exactly which model failed and why.

## 💡 Pro Tip for Beginners
Orchestration is the difference between a "Collection of Scripts" and a "System". Always aim to have your orchestration layer as the single source of truth for pipeline status.
