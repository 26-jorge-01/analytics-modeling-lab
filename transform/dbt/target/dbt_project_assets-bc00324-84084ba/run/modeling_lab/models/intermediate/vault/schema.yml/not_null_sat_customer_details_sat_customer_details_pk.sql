
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select sat_customer_details_pk
from "modeling_lab"."public"."sat_customer_details"
where sat_customer_details_pk is null



  
  
      
    ) dbt_internal_test