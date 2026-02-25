
    
    

with child as (
    select order_pk as from_field
    from "modeling_lab"."public"."link_order_customer"
    where order_pk is not null
),

parent as (
    select order_pk as to_field
    from "modeling_lab"."public"."hub_order"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


