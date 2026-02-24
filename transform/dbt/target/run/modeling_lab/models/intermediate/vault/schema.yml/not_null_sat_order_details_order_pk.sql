
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_pk
from "modeling_lab"."public"."sat_order_details"
where order_pk is null



  
  
      
    ) dbt_internal_test