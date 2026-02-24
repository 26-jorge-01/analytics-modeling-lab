
  create view "modeling_lab"."public"."stg_olist__customers__dbt_tmp"
    
    
  as (
    with source as (
    select * from "modeling_lab"."raw"."customers"
),

renamed as (
    select
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    from source
)

select * from renamed
  );