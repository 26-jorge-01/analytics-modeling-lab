
  create view "modeling_lab"."public"."stg_olist__category_translations__dbt_tmp"
    
    
  as (
    with source as (
    select * from "modeling_lab"."raw"."product_category_name_translation"
),

renamed as (
    select
        product_category_name,
        product_category_name_english
    from source
)

select * from renamed
  );