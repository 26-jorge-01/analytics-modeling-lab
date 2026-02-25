with customers as (
    select distinct customer_id
    from "modeling_lab"."public"."stg_olist__customers"
)

select
    customer_id as customer_bk,
    customer_id as customer_pk,
    'olist' as record_source,
    current_timestamp as load_date
from customers