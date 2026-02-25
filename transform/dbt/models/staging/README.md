# 🥉 Staging Layer: The Bronze Foundation

## 📖 How it Works
Staging is the first layer inside the Data Warehouse. Here, we mirror the source data but apply minimal, essential cleaning:
- **Type Casting**: Ensuring numbers are `numeric` and dates are `timestamp`.
- **Renaming**: Standardizing column names for consistency across sources.
- **Deduplication**: Filtering out obvious garbage or corrupted rows at the entry point.

## 🚀 Why it is Important (Industry)
- **Decoupling**: It protects the rest of the warehouse from changes in the source system. If the source changes a column name, you only fix it once in Staging.
- **Data Governance**: The first line of defense where "Data Contracts" are enforced.

## 🧪 Use Case in this Lab
We take raw Olist CSVs and turn them into clean dbt views. For example, `stg_olist__orders` ensures that all purchase timestamps are valid Postgres dates before they ever touch our expensive analytical models.

## 💡 Pro Tip for Beginners
**Never join staging models together.** Staging should always be a 1-to-1 reflection of a source table. Joins belong in the Intermediate/Core layer.
