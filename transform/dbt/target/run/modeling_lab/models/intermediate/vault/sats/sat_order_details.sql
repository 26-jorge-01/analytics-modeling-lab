
  
    

  create  table "modeling_lab"."public"."sat_order_details__dbt_tmp"
  
  
    as
  
  (
    with source as (
    select
        order_id as order_pk,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_customer_date,
        order_estimated_delivery_date,
        current_timestamp as load_date,
        'olist' as record_source
    from "modeling_lab"."public"."stg_olist__orders"
)

select
    md5(cast(coalesce(cast(order_pk as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(load_date as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as sat_order_details_pk,
    order_pk,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    load_date,
    record_source
from source
  );
  