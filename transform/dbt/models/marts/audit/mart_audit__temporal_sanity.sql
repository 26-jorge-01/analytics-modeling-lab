/*
This model discovers logical errors in procurement timelines.
Events should follow a natural order: Firma -> Inicio -> Fin.
*/

with staging as (
    select * from {{ ref('int_secop__standardized') }}
),

final as (
    select
        id_contrato,
        nombre_entidad,
        fecha_de_firma,
        fecha_de_inicio_del_contrato,
        fecha_de_fin_del_contrato,
        
        /* Logical Flags */
        case 
            when fecha_de_inicio_del_contrato > fecha_de_fin_del_contrato then true 
            else false 
        end as start_after_end,
        
        case 
            when fecha_de_firma > fecha_de_inicio_del_contrato then true 
            else false 
        end as signature_after_start,
        
        case 
            when fecha_de_firma < '2000-01-01' or fecha_de_firma > current_date + interval '1 year' then true 
            else false 
        end as suspicious_date
        
    from staging
    where fecha_de_firma is not null 
       or fecha_de_inicio_del_contrato is not null
)

select * from final
where start_after_end = true 
   or signature_after_start = true 
   or suspicious_date = true
