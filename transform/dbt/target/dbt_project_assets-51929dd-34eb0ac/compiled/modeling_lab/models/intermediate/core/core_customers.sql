with hubs as (
    select * from "modeling_lab"."public"."hub_customer"
),

sats as (
    select * from "modeling_lab"."public"."sat_customer_details"
),

latest_sats as (
    select *
    from (
        select 
            *,
            row_number() over (partition by customer_pk order by load_date desc) as rn
        from sats
    ) where rn = 1
)

select
    h.customer_id,
    s.customer_unique_id,
    s.customer_zip_code_prefix,
    s.customer_city,
    s.customer_state
from hubs h
inner join latest_sats s on h.customer_pk = s.customer_pk