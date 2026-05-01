{{ config(materialized='view') }}

with linkage as (
    select * from {{ ref('int_secop__agencies_linkage') }}
)

select
    raw_nit as original_nit,
    raw_name as original_name,
    compared_against_anchor as anchor_nit,
    compared_against_name as anchor_name,
    canonical_nit as resolved_nit,
    linkage_tier as resolution_method,
    algorithm_confidence
from linkage
where raw_nit != canonical_nit
order by algorithm_confidence asc
