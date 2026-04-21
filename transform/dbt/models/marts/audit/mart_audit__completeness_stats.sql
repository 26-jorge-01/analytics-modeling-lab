/*
This model provides a heatmap-ready view of missing data.
It helps discover which fields are actually usable for analysis.
*/

with staging as (
    select * from {{ ref('int_secop__standardized') }}
),

null_counts as (
    select
        anno_firma_contrato,
        count(*) as total_records,
        sum(case when id_contrato is null then 1 else 0 end) as null_id_contrato,
        sum(case when nit_entidad is null then 1 else 0 end) as null_nit_entidad,
        sum(case when documento_proveedor is null then 1 else 0 end) as null_documento_proveedor,
        sum(case when valor_del_contrato = 0 then 1 else 0 end) as zero_value_contracts,
        sum(case when fecha_de_firma is null then 1 else 0 end) as missing_signature_date,
        sum(case when modalidad_de_contratacion is null then 1 else 0 end) as missing_modality
    from staging
    group by 1
)

select 
    *,
    round(cast(null_id_contrato as numeric) / nullif(total_records, 0) * 100, 2) as pct_null_id,
    round(cast(zero_value_contracts as numeric) / nullif(total_records, 0) * 100, 2) as pct_zero_value
from null_counts
order by anno_firma_contrato desc
