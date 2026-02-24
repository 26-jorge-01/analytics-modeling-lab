
  
    

  create  table "modeling_lab"."public"."hub_order__dbt_tmp"
  
  
    as
  
  (
    with orders as (
    select distinct
        order_id as order_pk,
        order_id
    from "modeling_lab"."public"."stg_olist__orders"
)

select
    order_pk,
    order_id as order_bk,
    current_timestamp as load_date,
    'olist' as record_source
from orders
  );
  