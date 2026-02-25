with customer_orders as (
    select
        c.customer_unique_id,
        count(o.order_id) as total_orders,
        min(o.order_date) as first_order_date,
        max(o.order_date) as last_order_date,
        sum(o.total_value) as lifetime_value,
        avg(o.total_value) as avg_order_value
    from {{ ref('fct_order_item') }} as o
    inner join {{ ref('dim_customer') }} as c
        on o.customer_id = c.customer_id
    group by 1
),

final as (
    select
        customer_unique_id,
        total_orders,
        lifetime_value,
        avg_order_value,
        last_order_date,
        (current_date - last_order_date) as days_since_last_order,
        case
            when (current_date - last_order_date) > 90 then 1
            else 0
        end as is_churned_candidate
    from customer_orders
)

select * from final
