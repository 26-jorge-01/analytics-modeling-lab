with source as (
    select
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        customer_id as customer_pk,
        'olist' as record_source,
        current_timestamp as load_date
    from {{ ref('stg_olist__customers') }}
)

select
    customer_pk,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    record_source,
    load_date,
    {{ dbt_utils.generate_surrogate_key(['customer_pk', 'load_date']) }}
        as sat_customer_details_pk
from source
