with customers as (
    select distinct
        customer_id,
        customer_id as customer_pk
    from {{ ref('stg_olist__customers') }}
)

select
    customer_pk,
    customer_id as customer_bk,
    'olist' as record_source,
    current_timestamp as load_date
from customers
