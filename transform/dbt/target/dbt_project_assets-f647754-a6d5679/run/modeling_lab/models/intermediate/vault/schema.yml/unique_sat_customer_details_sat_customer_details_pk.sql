
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    sat_customer_details_pk as unique_field,
    count(*) as n_records

from "modeling_lab"."public"."sat_customer_details"
where sat_customer_details_pk is not null
group by sat_customer_details_pk
having count(*) > 1



  
  
      
    ) dbt_internal_test