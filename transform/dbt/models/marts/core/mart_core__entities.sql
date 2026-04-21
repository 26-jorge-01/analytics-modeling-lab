with staging as (
    select * from {{ ref('int_secop__standardized') }}
),

final as (
    select distinct
        codigo_entidad,
        nit_entidad,
        nombre_entidad,
        orden,
        rama,
        sector
    from staging
)

select * from final
