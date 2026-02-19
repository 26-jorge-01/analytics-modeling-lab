
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_id
from "modeling_lab"."public"."fct_order_item"
where customer_id is null



  
  
      
    ) dbt_internal_test