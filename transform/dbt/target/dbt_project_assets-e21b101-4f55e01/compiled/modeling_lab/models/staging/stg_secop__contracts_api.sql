with source as (
    select * from "modeling_lab"."raw"."raw_secop_api_contracts"
),

renamed as (
    select
        id_contrato as id_contrato,
        fecha_de_firma as fecha_firma,
        tipo_de_contrato as tipo_contrato,
        modalidad_de_contratacion as modalidad_contratacion,
        estado_contrato as estado_contrato,
        objeto_del_contrato as objeto_contrato,
        tipodocproveedor as tipo_doc_proveedor,
        documento_proveedor as documento_proveedor,
        proveedor_adjudicado as proveedor_adjudicado,
        tipo_de_identificaci_n_representante_legal as tipo_id_representante_legal,
        identificaci_n_representante_legal as id_representante_legal,
        nombre_representante_legal as nombre_representante_legal,
        nombre_entidad as nombre_entidad,
        nit_entidad as nit_entidad,
        departamento as departamento,
        ciudad as ciudad,
        valor_del_contrato as valor_contrato,
        urlproceso as url_proceso,
        -- Add placeholders for satellite consistency
        'NA'::text as proceso_compra,
        'NA'::text as referencia_contrato,
        'NA'::text as fecha_inicio_contrato,
        'NA'::text as fecha_fin_contrato,
        'NA'::text as ultima_actualizacion
    from source
),

ranked as (
    -- API records are unique by id_contrato in our current ingestion, 
    -- but we rank by fecha_firma as a fallback to match other models.
    select
        *,
        row_number() over (
            partition by id_contrato 
            order by fecha_firma desc
        ) as row_num
    from renamed
)

select * 
from ranked
where row_num = 1