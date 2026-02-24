
  
    

  create  table "modeling_lab"."public"."sat_customer_details__dbt_tmp"
  
  
    as
  
  (
    with source as (
    select
        customer_id as customer_pk,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        current_timestamp as load_date,
        'olist' as record_source
    from "modeling_lab"."public"."stg_olist__customers"
)

select
    md5(cast(coalesce(cast(customer_pk as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(load_date as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as sat_customer_details_pk,
    customer_pk,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    load_date,
    record_source
from source
  );
  