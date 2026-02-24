with orders as (
    select distinct
        order_id
    from {{ ref('stg_olist__orders') }}
)

select
    order_id as order_bk,
    order_id as order_pk,
    'olist' as record_source,
    current_timestamp as load_date
from orders
