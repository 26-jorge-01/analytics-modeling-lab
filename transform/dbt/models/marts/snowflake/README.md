# ❄️ Snowflake Model — Normalized Hierarchy for Operational Agility

> **Layer role:** Preserves referential integrity across geographic and organizational hierarchies. Designed for attributes that change frequently and require atomic, single-row updates.

---

## Models

| Model | Grain | Role in Hierarchy |
| :--- | :--- | :--- |
| `dim_state` | One row per Brazilian state | Root of geographic hierarchy |
| `dim_city` | One row per city/state combination | Mid-level hierarchy node |
| `dim_geography` | One row per zip code prefix | Leaf-level geographic entity |
| `dim_territory_management` | One row per zip code prefix (denormalized view) | Consumer-facing unified view |

---

## Why Not Just Flatten Geography into the Star Schema?

This is the right question to ask. The answer is in the **update propagation problem**:

Consider `region_manager` — an attribute of a state, assigned to a region. In a flat Star Schema, this attribute would appear in every row of `dim_customer` for every customer in that state. Olist has ~100k customers across 27 states.

| Action | Flat Star Schema | Snowflake Model |
| :--- | :--- | :--- |
| Change a Regional Manager | `UPDATE dim_customer SET region_manager = 'X' WHERE state = 'SP'` — tens of thousands of rows | `UPDATE dim_state SET region_manager = 'X' WHERE state_code = 'SP'` — **1 row** |
| Risk of inconsistency | High — partial update leaves corrupted state | Zero — atomicity guaranteed by single-row update |
| Rebuild cost | Full `dbt build` to re-materialize the dimension | `dbt build --select dim_state+` — only affected models |

At scale, this is the difference between a 2-minute routine operation and a multi-hour reprocessing job.

---

## `dim_territory_management` — The Consumer Interface

The normalized hierarchy introduces join complexity that operational users should not be exposed to. `dim_territory_management` resolves this by pre-joining the full hierarchy into a single flat view — providing the atomic-update guarantees of the Snowflake structure with the query simplicity of a Star Schema.

This pattern — **normalize for writes, denormalize for reads** — is a standard enterprise pattern for reference data management.

---

## References

- [Marts Overview](../README.md) — When to choose Snowflake vs Star
- [Star Schema](../star/README.md) — Contrasting approach for non-hierarchical dimensions
