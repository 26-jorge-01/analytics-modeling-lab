# 📥 Ingestion: The Entry Point

## 📖 How it Works
This project uses **Custom Python Scripts** (`extract_load.py`) for the ingestion phase. We extract data from raw CSV sources (Olist E-commerce dataset) and load it into the `raw` schema of our PostgreSQL database.

## 🚀 Why it is Important (Industry)
- **IDOMPOTENCY**: Our script ensures that re-running the ingestion doesn't create duplicate data. It cleans the target table before loading.
- **Flexibility**: While tools like Fivetran or Airbyte are great, custom scripts allow for specialized pre-cleaning and handled edge cases without additional license costs.
- **Schema Control**: We explicitly define the target schemas to ensure the "Raw" layer is isolated from the rest of the warehouse.

## 🧪 Use Case in this Lab
We handle the complex Olist dataset (9+ tables) efficiently. Our ingestion script acts as the "Gatekeeper", ensuring that the database is populated with valid raw data before the dbt transformation starts.

## 💡 Pro Tip for Beginners
In production, your ingestion should always be **observable**. Notice how we use logging and exception handling to ensure that if a CSV is missing or corrupted, the process stops immediately before poisoning the warehouse.
