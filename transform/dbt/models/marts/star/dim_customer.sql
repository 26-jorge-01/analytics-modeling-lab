with customers as (
    select * from {{ ref('core_customers') }}
)

select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix as zip_code_prefix
from customers
