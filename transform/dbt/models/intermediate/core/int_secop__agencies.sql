with source as (
    select * from {{ ref('int_secop__standardized') }}
),

ranked as (
    select
        nit_entidad,
        nombre_entidad,
        codigo_entidad,
        nivel_entidad,
        rama,
        sector,
        row_number() over (
            partition by nit_entidad 
            order by count(*) desc, max(ultima_actualizacion) desc
        ) as rank
    from source
    where nit_entidad is not null
    group by 
        nit_entidad, nombre_entidad, codigo_entidad, 
        nivel_entidad, rama, sector
),

agencies as (
    select
        {{ dbt_utils.generate_surrogate_key(['nit_entidad']) }} as agency_key,
        nit_entidad,
        nombre_entidad,
        codigo_entidad,
        nivel_entidad,
        rama,
        sector
    from ranked
    where rank = 1
)

select * from agencies
