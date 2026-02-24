with source as (
    select
        order_id as order_pk,
        customer_id as customer_pk,
        {{ dbt_utils.generate_surrogate_key(['order_id', 'customer_id']) }}
            as link_order_customer_pk
    from {{ ref('stg_olist__orders') }}
)

select
    order_pk,
    customer_pk,
    link_order_customer_pk,
    'olist' as record_source,
    current_timestamp as load_date
from source
