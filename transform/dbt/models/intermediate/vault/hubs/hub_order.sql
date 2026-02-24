with orders as (
    select distinct
        order_id,
        order_id as order_pk
    from {{ ref('stg_olist__orders') }}
)

select
    order_pk,
    order_id as order_bk,
    current_timestamp as load_date,
    'olist' as record_source
from orders
