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

overrides as (
    select * from {{ ref('stg_secop__agency_overrides') }}
),

-- Rank overrides: 1. Specific Name Match | 2. NIT-only Match
best_overrides as (
    select
        r.nit_entidad,
        r.nombre_entidad,
        o.override_subdivision_type,
        o.canonical_nit,
        o.canonical_name,
        row_number() over (
            partition by r.nit_entidad, r.nombre_entidad
            order by 
                (case when upper(trim(o.raw_name)) = upper(trim(r.nombre_entidad)) then 1 else 2 end),
                (case when o.raw_nit is not null then 1 else 2 end)
        ) as override_rank
    from raw_source r
    join overrides o on r.nit_entidad = o.raw_nit 
        and (o.raw_name is null or upper(trim(o.raw_name)) = upper(trim(r.nombre_entidad)))
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
        -- SUBDIVISION PARSER: Extract the functional unit from the name.
        -- Priority: 1. Manual Override (Name-Specific or NIT-General) | 2. Regex-based classification
        coalesce(
            nullif(o.override_subdivision_type, ''),
            case 
                when upper(coalesce(a.expanded_name, r.nombre_entidad)) ~* '\y(CONCEJO|PERSONERIA|CONTRALORIA)\y' 
                    then regexp_replace(upper(coalesce(a.expanded_name, r.nombre_entidad)), '.*(CONCEJO|PERSONERIA|CONTRALORIA).*', '\1', 'g')
                when upper(coalesce(a.expanded_name, r.nombre_entidad)) ~* '\y(SECRETARIA DE|SECRETARIA MUNICIPAL DE|SECRETARIA DISTRITAL DE)\y'
                    then 'SECRETARIA'
                -- Functional Departments (Careful exclusion of geographic names)
                when upper(coalesce(a.expanded_name, r.nombre_entidad)) ~* '\yDEPARTAMENTO\y' 
                     and upper(coalesce(a.expanded_name, r.nombre_entidad)) !~* ('\yDEPARTAMENTO (DE |DEL )?' || upper(coalesce(r.departamento, '')))
                    then 'DEPARTAMENTO'
                when upper(coalesce(a.expanded_name, r.nombre_entidad)) ~* '\y(REGIONAL|SECCIONAL)\y'
                    then 'REGIONAL'
                when upper(coalesce(a.expanded_name, r.nombre_entidad)) ~* '\y(TERRITORIAL|DIRECCION TERRITORIAL)\y'
                    then 'TERRITORIAL'
                when upper(coalesce(a.expanded_name, r.nombre_entidad)) ~* '\y(CENTRO ZONAL|CZ)\y'
                    then 'CENTRO ZONAL'
                when upper(coalesce(a.expanded_name, r.nombre_entidad)) ~* '\y(ALCALDIA LOCAL)\y'
                    then 'LOCALIDAD'
                else 'CENTRAL'
            end
        ) as subdivision_type,
        coalesce(o.canonical_nit, r.nit_entidad) as canonical_nit,
        o.canonical_name,
        case when o.canonical_nit is not null then true else false end as has_override,
        -- Extract base NIT for blocking
        split_part(r.nit_entidad, '-', 1) as base_nit,
        r.ultima_actualizacion
    from raw_source r
    left join acronyms a on upper(trim(r.nombre_entidad)) = upper(a.acronym)
    left join best_overrides o on r.nit_entidad = o.nit_entidad 
        and r.nombre_entidad = o.nombre_entidad
        and o.override_rank = 1
    where r.nit_entidad is not null
),

final as (
    select
        raw_nit,
        raw_name,
        canonical_nit,
        canonical_name,
        has_override,
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
        coalesce(ciudad, 'na') || '_' ||
        subdivision_type as smart_blocking_key,
        subdivision_type,

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
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
)

select * from final
