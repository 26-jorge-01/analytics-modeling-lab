with source as (
    select
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_customer_date,
        order_estimated_delivery_date,
        order_id as order_pk,
        'olist' as record_source,
        current_timestamp as load_date
    from {{ ref('stg_olist__orders') }}
)

select
    order_pk,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    record_source,
    load_date,
    {{ dbt_utils.generate_surrogate_key(['order_pk', 'load_date']) }}
        as sat_order_details_pk
from source
