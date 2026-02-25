
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_unique_id
from "modeling_lab"."public"."sat_customer_details"
where customer_unique_id is null



  
  
      
    ) dbt_internal_test