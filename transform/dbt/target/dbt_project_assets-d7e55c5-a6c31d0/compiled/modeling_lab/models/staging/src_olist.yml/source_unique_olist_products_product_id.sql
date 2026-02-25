
    
    

select
    product_id as unique_field,
    count(*) as n_records

from "modeling_lab"."raw"."products"
where product_id is not null
group by product_id
having count(*) > 1


