with source as (
    select
        md5(cast(coalesce(cast(order_id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(customer_id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as link_order_customer_pk,
        order_id as order_pk,
        customer_id as customer_pk
    from "modeling_lab"."public"."stg_olist__orders"
)

select
    link_order_customer_pk,
    order_pk,
    customer_pk,
    current_timestamp as load_date,
    'olist' as record_source
from source