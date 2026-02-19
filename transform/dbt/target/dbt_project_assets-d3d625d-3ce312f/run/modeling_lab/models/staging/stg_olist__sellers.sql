
  create view "modeling_lab"."public"."stg_olist__sellers__dbt_tmp"
    
    
  as (
    with source as (
    select * from "modeling_lab"."raw"."sellers"
),

renamed as (
    select
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state
    from source
)

select * from renamed
  );