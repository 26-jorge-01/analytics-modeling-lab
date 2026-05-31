{{
    config(
        materialized='incremental',
        unique_key='contract_fingerprint',
        on_schema_change='sync_all_columns'
    )
}}

with source as (
    select * from {{ ref('int_secop__standardized') }}
    {% if is_incremental() %}
        where ingested_at >= (select max(ingested_at) from {{ this }}) - interval '3 days'
    {% endif %}
),

-- Resolve agency_key by joining with golden agencies on (nit_entidad, departamento)
-- Also resolve location_key and vendor_key for consistency
agency_resolution as (
    select
        s.contract_fingerprint,
        a.agency_key,
        row_number() over (
            partition by s.contract_fingerprint 
            order by a.subdivision_type asc
        ) as rn
    from source s
    left join {{ ref('int_secop__agencies') }} a
        on s.nit_entidad = a.nit_entidad
        and s.departamento = a.departamento
),

resolved_keys as (
    select
        contract_fingerprint,
        agency_key
    from agency_resolution
    where rn = 1
),

final as (
    select
        /* Keys with null handling to ensure referential integrity */
        s.contract_fingerprint,
        
        rk.agency_key,
        
        case 
            when s.documento_proveedor is not null 
            then {{ dbt_utils.generate_surrogate_key(['s.documento_proveedor']) }}
            else null 
        end as vendor_key,
        
        case 
            when s.departamento is not null or s.municipio_de_obtencion is not null 
            then {{ dbt_utils.generate_surrogate_key(['s.departamento', 's.municipio_de_obtencion']) }}
            else null 
        end as location_key,

        /* Natural Keys (kept for convenience) */
        s.id_contrato,
        s.proceso_de_compra,
        s.nit_entidad,
        s.documento_proveedor,

        /* Dates & Financials */
        s.fecha_referencia,
        s.ultima_actualizacion,
        s.fecha_de_firma,
        s.fecha_de_inicio_del_contrato,
        s.fecha_de_fin_del_contrato,
        s.valor_del_contrato,
        s.valor_pagado,
        s.valor_amortizado,
        s.valor_facturado,
        s.valor_pendiente_de_pago,
        s.valor_total_de_adiciones,

        /* Categoricals (kept in fact for now) */
        s.modalidad_de_contratacion,
        s.tipo_de_contrato,
        s.estado_contrato,
        
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

    from source s
    left join resolved_keys rk on s.contract_fingerprint = rk.contract_fingerprint
)

select * from final
