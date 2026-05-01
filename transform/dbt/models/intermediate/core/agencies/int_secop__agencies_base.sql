{{ config(
    materialized='table',
    post_hook=[
        "create index if not exists idx_agencies_clean_name on {{ this }} using gist (clean_name_for_sim gist_trgm_ops)"
    ]
) }}

with raw_source as (
    select * from {{ ref('int_secop__standardized') }}
),

acronyms as (
    select * from {{ ref('stg_secop__acronyms') }}
),

source as (
    select
        r.nit_entidad as raw_nit,
        r.nombre_entidad as raw_name,
        r.codigo_entidad,
        r.nivel_entidad,
        r.rama,
        r.sector,
        r.departamento,
        r.ciudad,
        -- Expand Acronyms if a match is found in our dictionary
        coalesce(a.expanded_name, r.nombre_entidad) as expanded_name,
        -- Extract base NIT for blocking
        split_part(r.nit_entidad, '-', 1) as base_nit,
        r.ultima_actualizacion
    from raw_source r
    left join acronyms a on upper(trim(r.nombre_entidad)) = upper(a.acronym)
    where r.nit_entidad is not null
),

final as (
    select
        raw_nit,
        raw_name,
        codigo_entidad,
        nivel_entidad,
        rama,
        sector,
        departamento,
        ciudad,
        base_nit,
        -- Smart Blocking Key: Always incorporates geography to prevent collisions 
        -- even for 9-digit NITs that might be reused across different territorial entities.
        base_nit || '_' || 
        coalesce(departamento, 'na') || '_' || 
        coalesce(ciudad, 'na') as smart_blocking_key,
        -- Cleansing logic for Entity Resolution:
        -- 1. Remove punctuation (dots, commas)
        -- 2. Strip generic prefixes (ALCALDIA, MUNICIPIO, etc.)
        -- 3. Strip legal suffixes (SAS, ESP, LTDA, EN LIQUIDACION, etc.)
        -- 4. Collapse multiple spaces
        trim(regexp_replace(
            regexp_replace(
                regexp_replace(
                    regexp_replace(
                        upper(expanded_name), 
                        '[.,]', '', 'g'
                    ),
                    '\y(ALCALDIA|MUNICIPIO|MUNICIPAL|DE|LA|EL|LOS|LAS|GOBERNACION|INSTITUCION|EDUCATIVA|IE|CENTRO|PERSONERIA)\y', '', 'g'
                ),
                '\y(SAS|SA|ESP|EICE|EP|LTDA|LIMITADA|S EN C|SCA|EU|EN LIQUIDACION|EN REORGANIZACION|SOCIEDAD ANONIMA|EMPRESA DE SERVICIOS PUBLICOS)\y', '', 'g'
            ),
            '\s+', ' ', 'g'
        )) as clean_name_for_sim,
        count(*) as num_contracts,
        max(ultima_actualizacion) as ultima_actualizacion
    from source
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
)

select * from final
