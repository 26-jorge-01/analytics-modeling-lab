
  
    

  create  table "modeling_lab"."public"."dim_product__dbt_tmp"
  
  
    as
  
  (
    with products as (
    select * from "modeling_lab"."public"."core_products"
),

joined as (
    select
        p.product_id,
        coalesce(p.product_category_name_english, p.product_category_name) as product_category,
        p.product_name_lenght,
        p.product_description_lenght,
        p.product_photos_qty,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    from products p
)

select * from joined
  );
  