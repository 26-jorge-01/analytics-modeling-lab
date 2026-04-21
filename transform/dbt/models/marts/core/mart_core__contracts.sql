with staging as (
    select * from {{ ref('int_secop__standardized') }}
),

final as (
    select
        id_contrato,
        codigo_entidad,
        documento_proveedor,
        proceso_de_compra,
        
        /* Financials */
        valor_del_contrato,
        valor_pagado,
        valor_total_de_adiciones,
        
        /* Temporals */
        fecha_referencia,
        fecha_de_firma,
        fecha_de_inicio_del_contrato,
        fecha_de_fin_del_contrato,
        
        /* Categoricals */
        estado_contrato,
        tipo_de_contrato,
        modalidad_de_contratacion,
        
        /* Geography */
        departamento,
        municipio_de_obtencion
    from staging
)

select * from final
