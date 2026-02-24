with customers as (
    select distinct
        customer_id
    from {{ ref('stg_olist__customers') }}
)

select
    customer_id as customer_bk,
    'olist' as record_source,
    current_timestamp as load_date
from customers
