
    
    

with child as (
    select customer_pk as from_field
    from "modeling_lab"."public"."link_order_customer"
    where customer_pk is not null
),

parent as (
    select customer_pk as to_field
    from "modeling_lab"."public"."hub_customer"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


