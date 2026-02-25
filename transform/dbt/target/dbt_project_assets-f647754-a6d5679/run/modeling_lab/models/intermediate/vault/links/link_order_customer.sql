
  
    

  create  table "modeling_lab"."public"."link_order_customer__dbt_tmp"
  
  
    as
  
  (
    with source as (
    select
        order_id as order_pk,
        customer_id as customer_pk,
        md5(cast(coalesce(cast(order_id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(customer_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT))
            as link_order_customer_pk
    from "modeling_lab"."public"."stg_olist__orders"
)

select
    order_pk,
    customer_pk,
    link_order_customer_pk,
    'olist' as record_source,
    current_timestamp as load_date
from source
  );
  