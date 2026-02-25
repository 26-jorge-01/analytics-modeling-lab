
  
    

  create  table "modeling_lab"."public"."fct_order_experience__dbt_tmp"
  
  
    as
  
  (
    with order_logistics as (
    select
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_delivered_customer_date,
        order_estimated_delivery_date,
        extract(day from order_delivered_customer_date - order_purchase_timestamp) as actual_delivery_days,
        extract(day from order_estimated_delivery_date - order_purchase_timestamp) as estimated_delivery_days,
        extract(day from order_delivered_customer_date - order_estimated_delivery_date) as delivery_delay_days
    from "modeling_lab"."public"."core_orders"
    where order_status = 'delivered'
),

reviews as (
    select
        order_id,
        review_score,
        review_comment_message
    from "modeling_lab"."raw"."order_reviews"
),

final as (
    select
        ol.*,
        r.review_score,
        case
            when ol.delivery_delay_days > 0 then 1
            else 0
        end as is_late_delivery,
        case
            when r.review_score <= 2 then 1
            else 0
        end as is_negative_review
    from order_logistics ol
    left join reviews r on ol.order_id = r.order_id
)

select * from final
  );
  