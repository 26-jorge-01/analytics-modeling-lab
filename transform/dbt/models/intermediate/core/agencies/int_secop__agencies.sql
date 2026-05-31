{{ config(materialized='table') }}

with base as (
    select * from {{ ref('int_secop__agencies_base') }}
),

linkage as (
    select * from {{ ref('int_secop__agencies_linkage') }}
),

-- 1. Operational Survivorship: Pick the "Golden" attributes for each functional unit
ranked_operational as (
    select 
        l.canonical_nit,
        l.subdivision_type,
        b.departamento,
        coalesce(b.canonical_name, b.raw_name) as golden_name,
        b.codigo_entidad as golden_codigo,
        b.nivel_entidad as golden_nivel,
        b.rama as golden_rama,
        b.sector as golden_sector,
        b.num_contracts,
        b.ultima_actualizacion,
        row_number() over (
            partition by l.canonical_nit, l.subdivision_type, b.departamento
            order by 
                (case when b.canonical_name is not null then 1 else 2 end),
                b.num_contracts desc, 
                b.ultima_actualizacion desc
        ) as rn
    from linkage l
    join base b on l.raw_nit = b.raw_nit and l.smart_blocking_key = b.smart_blocking_key
),

-- 2. Legal Survivorship: Pick the "Global" name for the NIT (The Roll-up name)
legal_parents as (
    select 
        canonical_nit,
        golden_name as nombre_parent,
        row_number() over (
            partition by canonical_nit 
            order by 
                (case when subdivision_type = 'CENTRAL' then 1 else 2 end),
                rn asc
        ) as rn_parent
    from ranked_operational
    where rn = 1
),

final_agencies as (
    select
        {{ dbt_utils.generate_surrogate_key(['op.canonical_nit', 'op.subdivision_type', 'op.departamento']) }} as agency_key,
        op.canonical_nit as nit_entidad,
        op.golden_name as nombre_entidad,
        lp.nombre_parent,
        op.subdivision_type,
        op.golden_codigo as codigo_entidad,
        op.golden_nivel as nivel_entidad,
        op.golden_rama as rama,
        op.golden_sector as sector,
        op.departamento
    from ranked_operational op
    join legal_parents lp on op.canonical_nit = lp.canonical_nit and lp.rn_parent = 1
    where op.rn = 1
)

select * from final_agencies
