with orders as (
    select distinct
        order_id,
        order_id as order_pk
    from {{ ref('stg_olist__orders') }}
)

select
    order_pk,
    order_id as order_bk,
    'olist' as record_source,
    current_timestamp as load_date
from orders
