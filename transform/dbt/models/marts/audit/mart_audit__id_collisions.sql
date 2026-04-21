/* 
This model identifies cases where the same ID_CONTRATO is reused 
across different entities or suppliers. This helps visualize 
the "Identity Crisis" in the raw data.
*/

with staging as (
    select * from {{ ref('int_secop__standardized') }}
),

collision_check as (
    select
        id_contrato,
        count(distinct codigo_entidad) as entity_count,
        count(distinct nit_entidad) as nit_count,
        count(distinct documento_proveedor) as supplier_count,
        count(distinct proceso_de_compra) as process_count,
        count(*) as row_count
    from staging
    group by 1
),

final as (
    select
        s.id_contrato,
        s.nombre_entidad,
        s.proveedor_adjudicado as nombre_del_proveedor,
        s.proceso_de_compra,
        s.valor_del_contrato,
        c.entity_count,
        c.supplier_count,
        c.process_count,
        c.row_count,
        
        case 
            when c.entity_count > 1 then 'Cross-Entity Collision'
            when c.process_count > 1 then 'Multi-Process Collision'
            when c.supplier_count > 1 then 'Supplier Dispute/Split'
            else 'Unique'
        end as discovery_flag
    from staging s
    join collision_check c on s.id_contrato = c.id_contrato
    where c.row_count > 1
)

select * from final
order by id_contrato
