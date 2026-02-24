with products as (
    select * from "modeling_lab"."public"."stg_olist__products"
),

categories as (
    select * from "modeling_lab"."public"."stg_olist__category_translations"
)

select
    p.product_id,
    p.product_category_name,
    c.product_category_name_english,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
from products p
left join categories c on p.product_category_name = c.product_category_name