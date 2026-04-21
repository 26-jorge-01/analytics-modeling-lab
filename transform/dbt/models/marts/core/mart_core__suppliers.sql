with staging as (
    select * from {{ ref('int_secop__standardized') }}
),

final as (
    select distinct
        documento_proveedor,
        proveedor_adjudicado as nombre_del_proveedor,
        tipodocproveedor as tipo_identificacion
    from staging
)

select * from final
