
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_date
from "modeling_lab"."public"."fct_order_item"
where order_date is null



  
  
      
    ) dbt_internal_test