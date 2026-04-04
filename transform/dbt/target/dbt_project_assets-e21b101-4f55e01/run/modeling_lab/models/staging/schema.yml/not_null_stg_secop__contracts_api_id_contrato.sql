
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_contrato
from "modeling_lab"."public"."stg_secop__contracts_api"
where id_contrato is null



  
  
      
    ) dbt_internal_test