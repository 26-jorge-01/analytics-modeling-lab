
  
    

  create  table "modeling_lab"."public"."core_order_items__dbt_tmp"
  
  
    as
  
  (
    with order_items as (
    select * from "modeling_lab"."public"."stg_olist__order_items"
)

select
    md5(cast(coalesce(cast(order_id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(order_item_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT))
        as order_item_key,
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
from order_items
  );
  