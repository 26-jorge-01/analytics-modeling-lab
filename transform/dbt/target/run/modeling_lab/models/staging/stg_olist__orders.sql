
  create view "modeling_lab"."public"."stg_olist__orders__dbt_tmp"
    
    
  as (
    with source as (
    select * from "modeling_lab"."raw"."orders"
),

renamed as (
    select
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date
    from source
)

select * from renamed
  );