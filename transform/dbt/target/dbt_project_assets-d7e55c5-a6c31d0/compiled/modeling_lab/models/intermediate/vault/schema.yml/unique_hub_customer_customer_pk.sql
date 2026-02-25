
    
    

select
    customer_pk as unique_field,
    count(*) as n_records

from "modeling_lab"."public"."hub_customer"
where customer_pk is not null
group by customer_pk
having count(*) > 1


