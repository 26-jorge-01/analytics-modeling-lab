
  create view "modeling_lab"."public"."stg_olist__order_payments__dbt_tmp"
    
    
  as (
    with source as (
    select * from "modeling_lab"."raw"."order_payments"
),

renamed as (
    select
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value
    from source
)

select * from renamed
  );