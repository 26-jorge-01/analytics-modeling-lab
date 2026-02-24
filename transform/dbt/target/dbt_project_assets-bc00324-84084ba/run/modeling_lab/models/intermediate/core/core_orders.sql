
  
    

  create  table "modeling_lab"."public"."core_orders__dbt_tmp"
  
  
    as
  
  (
    with hubs as (
    select * from "modeling_lab"."public"."hub_order"
),

sats as (
    select * from "modeling_lab"."public"."sat_order_details"
),

latest_sats as (
    select *
    from (
        select 
            *,
            row_number() over (partition by order_pk order by load_date desc) as rn
        from sats
    ) where rn = 1
)

select
    h.order_bk as order_id,
    -- Note: core_orders usually joins with hub_customer/link to get customer_id
    -- For simplicity in this demo, we can get it from the link or the sat if it was there
    -- Let's use the link to demonstrate the DV power
    l.customer_pk as customer_id, 
    s.order_status,
    s.order_purchase_timestamp,
    s.order_approved_at,
    s.order_delivered_customer_date,
    s.order_estimated_delivery_date
from hubs h
inner join latest_sats s on h.order_pk = s.order_pk
inner join "modeling_lab"."public"."link_order_customer" l on h.order_pk = l.order_pk
  );
  