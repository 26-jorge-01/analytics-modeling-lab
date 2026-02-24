with customers as (
    select distinct
        customer_id as customer_pk,
        customer_id
    from {{ ref('stg_olist__customers') }}
)

select
    customer_id as customer_bk,
    customer_pk,
    current_timestamp as load_date,
    'olist' as record_source
from customers
