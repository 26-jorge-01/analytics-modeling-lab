# 🏛️ Core Layer: The Integration Hub (3NF)

## 📖 How it Works
The Core layer implements **Third Normal Form (3NF)** logic. Here, we decouple the data from its source-specific formats and integrate it into a single, clean business model. We ensure that:
- Every entity has a unique business key.
- There are no repeating groups or data redundancies.
- Relationships (Foreign Keys) are strictly enforced.

## 🚀 Why it is Important (Industry)
- **Source of Truth**: This is the most reliable place to answer complex operational questions.
- **Data Integrity**: By normalizing, we prevent "Update Anomalies" where data represents different things in different places.
- **Reference Standard**: Used as the foundation for both Star Schemas and complex analytical views.

## 🧪 Use Case in this Lab
Models like `core_customers` and `core_orders` take the highly redundant Olist CSV data and organize it into clean, relational tables. If a customer changes their city, we only have one place to verify that change across all orders.

## 💡 Pro Tip for Beginners
If your "Marts" are getting too complex and slow to build, it's usually because you skipped the Core layer. A strong 3NF core makes all subsequent modeling (Star, Snowflake) 10x easier to maintain.
