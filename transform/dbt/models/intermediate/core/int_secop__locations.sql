with source as (
    select * from {{ ref('int_secop__standardized') }}
),

ranked as (
    select
        departamento,
        municipio_de_obtencion,
        row_number() over (
            partition by departamento, municipio_de_obtencion 
            order by count(*) desc
        ) as rank
    from source
    where departamento is not null 
       or municipio_de_obtencion is not null
    group by departamento, municipio_de_obtencion
),

locations as (
    select
        {{ dbt_utils.generate_surrogate_key(['departamento', 'municipio_de_obtencion']) }} as location_key,
        departamento,
        municipio_de_obtencion
    from ranked
    where rank = 1
)

select * from locations
