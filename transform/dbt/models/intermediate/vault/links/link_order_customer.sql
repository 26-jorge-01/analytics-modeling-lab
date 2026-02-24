with source as (
    select
        {{ dbt_utils.generate_surrogate_key(['order_id', 'customer_id']) }} as link_order_customer_pk,
        order_id as order_pk,
        customer_id as customer_pk
    from {{ ref('stg_olist__orders') }}
)

select
    link_order_customer_pk,
    order_pk,
    customer_pk,
    current_timestamp as load_date,
    'olist' as record_source
from source
