{{ config(materialized='table') }}

with base as (
    select * from {{ ref('int_secop__agencies_base') }}
),

linkage as (
    select * from {{ ref('int_secop__agencies_linkage') }}
),

-- Survivorship: Pick the "Golden" attributes for the canonical cluster
ranked_golden as (
    select 
        l.canonical_nit,
        b.raw_name as golden_name,
        b.codigo_entidad as golden_codigo,
        b.nivel_entidad as golden_nivel,
        b.rama as golden_rama,
        b.sector as golden_sector,
        row_number() over (
            partition by l.canonical_nit 
            order by b.num_contracts desc, b.ultima_actualizacion desc
        ) as rn
    from linkage l
    join base b on l.raw_nit = b.raw_nit
),

final_agencies as (
    select
        {{ dbt_utils.generate_surrogate_key(['canonical_nit']) }} as agency_key,
        canonical_nit as nit_entidad,
        golden_name as nombre_entidad,
        golden_codigo as codigo_entidad,
        golden_nivel as nivel_entidad,
        golden_rama as rama,
        golden_sector as sector
    from ranked_golden
    where rn = 1
)

select * from final_agencies
