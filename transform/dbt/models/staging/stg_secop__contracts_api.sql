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
        -- 1. Explicitly cast/rename core fields for standard downstream use
        id_contrato as id_contrato_core,
        proceso_de_compra as proceso_compra_core,
        nit_entidad as nit_entidad_core,
        documento_proveedor as documento_proveedor_core,
        fecha_de_firma::timestamp as fecha_firma_core,
        ultima_actualizacion::timestamp as ultima_actualizacion_core,
        valor_del_contrato::numeric as valor_contrato_core,
        
        -- 2. Preserve ALL raw columns as-is (Zero-Loss)
        *
    from ranked
    where row_num = 1
)

select * from final
