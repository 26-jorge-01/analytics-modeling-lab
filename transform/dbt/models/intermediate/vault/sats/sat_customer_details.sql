with source as (
    select
        customer_id as customer_pk,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        current_timestamp as load_date,
        'olist' as record_source
    from {{ ref('stg_olist__customers') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['customer_pk', 'load_date']) }} as sat_customer_details_pk,
    customer_pk,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    load_date,
    record_source
from source
