
    
    

select
    id_contrato as unique_field,
    count(*) as n_records

from "modeling_lab"."public"."stg_secop__contracts_api"
where id_contrato is not null
group by id_contrato
having count(*) > 1


