
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_pk
from "modeling_lab"."public"."link_order_customer"
where customer_pk is null



  
  
      
    ) dbt_internal_test