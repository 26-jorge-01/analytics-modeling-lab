# ❄️ Snowflake Model: The Operational Efficiency Layer

## 📖 How it Works
A Snowflake Model is a variation of the Star Schema where **dimensions are normalized** into multiple related tables. Instead of one flat "Geography" table, we have a hierarchy: `dim_state` -> `dim_city` -> `dim_geography` (Zip Code).

## 🚀 Why it is Important (Industry)
- **Data Integrity**: Eliminates redundancy at the dimension level.
- **Atomic Updates**: Changing an attribute at a high level (e.g., a State's Tax Rate) only requires a single row update.
- **Small Footprint**: Efficient storage by not repeating long string values across millions of rows.

## 🧪 Business Case in this Lab (Territory Management)
We use the Snowflake hierarchy to manage **Territory Operations**.
- **The Problem**: In a flat schema, updating a "Regional Sales Manager" for the state of São Paulo requires updating millions of rows in the geography dimension.
- **The Solution**: By normalizing into `dim_state`, we update **1 row**. The change propagates instantly to all joined reports, demonstrating superior operational agility.

## 💡 Pro Tip for Beginners
Snowflake models are often criticized for join complexity, but they are essential when your dimension attributes (like Tax Rates or Sales Territories) change frequently and you need to preserve historical accuracy without massive data duplication.
