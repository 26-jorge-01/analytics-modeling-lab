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
    from {{ ref('stg_olist__orders') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['order_pk', 'load_date']) }} as sat_order_details_pk,
    order_pk,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    load_date,
    record_source
from source
