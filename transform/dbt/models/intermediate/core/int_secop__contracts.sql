with source as (
    select * from {{ ref('int_secop__standardized') }}
),

final as (
    select
        /* Keys with null handling to ensure referential integrity */
        contract_fingerprint,
        
        case 
            when nit_entidad is not null then {{ dbt_utils.generate_surrogate_key(['nit_entidad']) }}
            else null 
        end as agency_key,
        
        case 
            when documento_proveedor is not null then {{ dbt_utils.generate_surrogate_key(['documento_proveedor']) }}
            else null 
        end as vendor_key,
        
        case 
            when departamento is not null or municipio_de_obtencion is not null 
            then {{ dbt_utils.generate_surrogate_key(['departamento', 'municipio_de_obtencion']) }}
            else null 
        end as location_key,

        /* Natural Keys (kept for convenience) */
        id_contrato,
        proceso_de_compra,
        nit_entidad,
        documento_proveedor,

        /* Dates & Financials */
        fecha_referencia,
        ultima_actualizacion,
        fecha_de_firma,
        fecha_de_inicio_del_contrato,
        fecha_de_fin_del_contrato,
        valor_del_contrato,
        valor_pagado,
        valor_amortizado,
        valor_facturado,
        valor_pendiente_de_pago,
        valor_total_de_adiciones,

        /* Categoricals (kept in fact for now) */
        modalidad_de_contratacion,
        tipo_de_contrato,
        estado_contrato,
        
        /* All other fields from standardized except the ones moved to dims */
        {{ dbt_utils.star(
            from=ref('int_secop__standardized'),
            except=[
                'contract_fingerprint', 'nit_entidad', 'documento_proveedor', 'id_contrato', 'proceso_de_compra',
                'nombre_entidad', 'codigo_entidad', 'proveedor_adjudicado', 'departamento', 'municipio_de_obtencion',
                'fecha_referencia', 'ultima_actualizacion', 'fecha_de_firma', 'fecha_de_inicio_del_contrato', 
                'fecha_de_fin_del_contrato', 'valor_del_contrato', 'valor_pagado', 'valor_amortizado', 
                'valor_facturado', 'valor_pendiente_de_pago', 'valor_total_de_adiciones',
                'modalidad_de_contratacion', 'tipo_de_contrato', 'estado_contrato',
                'nivel_entidad', 'rama', 'sector',
                'tipodocproveedor', 'es_pyme', 'tama_o_mipyme'
            ]
        ) }}

    from source
)

select * from final
