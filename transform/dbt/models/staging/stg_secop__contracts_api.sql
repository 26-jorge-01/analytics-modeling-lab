with source as (
    select * from {{ source('secop', 'raw_secop_api_contracts') }}
),

ranked as (
    /* 
    Deduplication using a composite natural key to handle ID reuse 
    and dual-watermarking for versioning.
    */
    select
        *,
        row_number() over (
            partition by 
                id_contrato, 
                proceso_de_compra, 
                nit_entidad, 
                documento_proveedor
            order by 
                coalesce(ultima_actualizacion, '1900-01-01') desc, 
                fecha_de_firma desc
        ) as row_num
    from source
),

final as (
    select
        /* 
        1. Core Identification (Business Keys)
        Using original names with consistent types for cross-layer joins.
        */
        cast(id_contrato as text) as id_contrato,
        cast(proceso_de_compra as text) as proceso_de_compra,
        cast(nit_entidad as text) as nit_entidad,
        cast(documento_proveedor as text) as documento_proveedor,
        cast(codigo_entidad as text) as codigo_entidad,
        
        /* 
        2. High-Precision Financial Metrics
        Using DECIMAL(20, 4) for BI-grade reliability.
        */
        cast(coalesce(valor_del_contrato, 0) as decimal(20, 4)) as valor_del_contrato,
        cast(coalesce(valor_pagado, 0) as decimal(20, 4)) as valor_pagado,
        cast(coalesce(valor_amortizado, 0) as decimal(20, 4)) as valor_amortizado,
        cast(coalesce(valor_facturado, 0) as decimal(20, 4)) as valor_facturado,
        cast(coalesce(valor_pendiente_de_pago, 0) as decimal(20, 4)) as valor_pendiente_de_pago,
        cast(coalesce(valor_total_de_adiciones, 0) as decimal(20, 4)) as valor_total_de_adiciones,
        cast(coalesce(valor_rubro, 0) as decimal(20, 4)) as valor_rubro,
        cast(coalesce(valor_de_pago_adelantado, 0) as decimal(20, 4)) as valor_de_pago_adelantado,
        cast(coalesce(valor_pendiente_de, 0) as decimal(20, 4)) as valor_pendiente_de,
        cast(coalesce(valor_pendiente_de_ejecucion, 0) as decimal(20, 4)) as valor_pendiente_de_ejecucion,
        cast(coalesce(cast(nullif(cuantia_contrato, '') as decimal(20, 4)), 0) as decimal(20, 4)) as cuantia_contrato,
        
        /* 
        3. Standardized Temporals
        Implementing fallback logic: Signature Date -> Start Date -> Update Watermark.
        */
        cast(coalesce(
            cast(fecha_de_firma as timestamp), 
            cast(fecha_de_inicio_del_contrato as timestamp), 
            ultima_actualizacion
        ) as timestamp) as fecha_referencia,
        
        cast(ultima_actualizacion as timestamp) as ultima_actualizacion,
        cast(fecha_de_firma as timestamp) as fecha_de_firma,
        cast(fecha_de_inicio_del_contrato as timestamp) as fecha_de_inicio_del_contrato,
        cast(fecha_de_fin_del_contrato as timestamp) as fecha_de_fin_del_contrato,
        cast(fecha_de_cargue_en_el_secop as timestamp) as fecha_de_cargue_en_el_secop,
        cast(fecha_inicio_liquidacion as timestamp) as fecha_inicio_liquidacion,
        
        /* 
        4. Raw Categoricals (DV-Ready)
        Preserving original casing for downstream 3NF/DV layers.
        */
        cast(modalidad_de_contratacion as text) as modalidad_de_contratacion,
        cast(tipo_de_contrato as text) as tipo_de_contrato,
        cast(municipio_de_obtencion as text) as municipio_de_obtencion,
        cast(departamento as text) as departamento,
        cast(estado_contrato as text) as estado_contrato,

        /*
        5. Integer fields
        */
        cast(coalesce(cast(nullif(anno_cargue_secop, '') as integer), 0) as integer) as anno_cargue_secop,
        cast(coalesce(cast(nullif(anno_firma_contrato, '') as integer), 0) as integer) as anno_firma_contrato,
        cast(coalesce(cast(nullif(id_modalidad, '') as integer), 0) as integer) as id_modalidad,
        cast(coalesce(cast(nullif(id_regimen_de_contratacion, '') as integer), 0) as integer) as id_regimen_de_contratacion,
        cast(coalesce(cast(nullif(id_sub_unidad_ejecutora, '') as integer), 0) as integer) as id_sub_unidad_ejecutora,

        /* 
        6. Zero-Loss Field Preservation
        Including all other raw columns automatically using dbt_utils.star.
        This avoids naming collisions while ensuring 100% data availability.
        */
        {{ dbt_utils.star(
            from=source('secop', 'raw_secop_api_contracts'), 
            except=[
                'id_contrato', 'proceso_de_compra', 'nit_entidad', 'documento_proveedor', 'codigo_entidad',
                'valor_del_contrato', 'valor_pagado', 'valor_amortizado', 'valor_facturado', 'valor_pendiente_de_pago',
                'ultima_actualizacion', 'fecha_de_firma', 'fecha_de_inicio_del_contrato', 'fecha_de_fin_del_contrato',
                'modalidad_de_contratacion', 'tipo_de_contrato', 'municipio_de_obtencion', 'departamento', 'estado_contrato',
                'anno_cargue_secop', 'anno_firma_contrato', 'id_modalidad', 'id_regimen_de_contratacion',
                'fecha_de_cargue_en_el_secop', 'cuantia_contrato', 'id_sub_unidad_ejecutora', 'fecha_inicio_liquidacion',
                'valor_total_de_adiciones', 'valor_rubro', 'valor_de_pago_adelantado', 'valor_pendiente_de', 'valor_pendiente_de_ejecucion'
            ]
        ) }}

    from ranked
    where row_num = 1
)

select * from final
