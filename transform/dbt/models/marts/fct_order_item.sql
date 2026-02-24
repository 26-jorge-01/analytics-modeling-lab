with orders as (
    select * from {{ ref('core_orders') }}
),

order_items as (
    select * from {{ ref('core_order_items') }}
),

joined as (
    select
        -- Keys
        oi.order_item_key,
        oi.order_id,
        oi.order_item_id,
        o.customer_id,
        oi.product_id,
        oi.seller_id,
        
        -- Dates
        cast(o.order_purchase_timestamp as date) as order_date,
        
        -- Dimensions from orders
        o.order_status,
        
        -- Measures
        oi.price,
        oi.freight_value,
        (oi.price + oi.freight_value) as total_value

    from order_items as oi
    inner join orders as o
        on oi.order_id = o.order_id
)

select * from joined
