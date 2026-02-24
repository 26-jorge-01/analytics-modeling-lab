
    
    

with child as (
    select order_date as from_field
    from "modeling_lab"."public"."fct_order_item"
    where order_date is not null
),

parent as (
    select date_key as to_field
    from "modeling_lab"."public"."dim_date"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


