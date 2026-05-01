{{ config(materialized='table') }}

with linkage as (
    select * from {{ ref('int_secop__agencies_linkage') }}
),

base as (
    select * from {{ ref('int_secop__agencies_base') }}
),

-- Aggregate agency-level metrics by the resolved Canonical NIT
agency_metrics as (
    select
        canonical_nit,
        sum(num_contracts) as total_contracts,
        max(ultima_actualizacion) as last_updated
    from linkage
    group by 1
),

-- Identify the "Golden Name" (The name of the anchor for each canonical group)
golden_names as (
    select 
        canonical_nit,
        compared_against_name as golden_name,
        compared_against_anchor as anchor_nit
    from linkage
    where raw_nit = canonical_nit -- The record itself is the representative
    qualify row_number() over (partition by canonical_nit order by linkage_tier asc) = 1
),

-- Enrich with metadata from the base table
agency_metadata as (
    select
        l.canonical_nit,
        b.nivel_entidad,
        b.rama,
        b.sector,
        b.departamento,
        b.ciudad,
        row_number() over (partition by l.canonical_nit order by b.num_contracts desc) as metadata_rank
    from linkage l
    join base b on l.raw_nit = b.raw_nit
)

select
    n.canonical_nit,
    n.golden_name,
    m.total_contracts,
    meta.nivel_entidad,
    meta.rama,
    meta.sector,
    meta.departamento,
    meta.ciudad,
    m.last_updated
from golden_names n
join agency_metrics m on n.canonical_nit = m.canonical_nit
join agency_metadata meta on n.canonical_nit = meta.canonical_nit
where meta.metadata_rank = 1
