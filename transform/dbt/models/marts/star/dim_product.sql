with products as (
    select * from {{ ref('core_products') }}
),

joined as (
    select
        p.product_id,
        p.product_name_lenght,
        p.product_description_lenght,
        p.product_photos_qty,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm,
        coalesce(
            p.product_category_name_english, p.product_category_name
        ) as product_category
    from products as p
)

select * from joined
