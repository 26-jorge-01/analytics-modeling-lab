# 🏗️ Transformation Layer: The dbt Engine

## 📊 Modeling Strategy
This directory contains the heart of our data transformation logic. We follow a **Multi-Layer Architecture** (often called Medallion) to ensure data moves from raw instability to refined business value.

### 🗺️ The Layers
1. **[Staging](./models/staging/) (Bronze)**: Cleaning & Type Casting.
2. **[Intermediate](./models/intermediate/) (Silver)**:
    - **[Core](./models/intermediate/core/)**: 3NF Integration.
    - **[Vault](./models/intermediate/vault/)**: Data Vault 2.0 History.
3. **[Marts](./models/marts/) (Gold)**: Paradigm-specific consumption layers (Star, Snowflake, Galaxy).

## 🛠️ dbt Best Practices in this Lab
- **Ephemeral & Incremental**: We use `views` for agility in staging and `tables` for performance in marts.
- **Surrogate Keys**: We use `dbt_utils.generate_surrogate_key` to create deterministic IDs because transactional systems don't always provide reliable PKs.
- **Documentation**: Every model and column is documented in `schema.yml` files (like the one in [marts/star/](./models/marts/star/schema.yml)).

## 💡 Why dbt?
dbt (Data Build Tool) allows us to write modular SQL with the power of software engineering (Version Control, Testing, Dry logic). It turns SQL scripts into a living, documented ecosystem.
