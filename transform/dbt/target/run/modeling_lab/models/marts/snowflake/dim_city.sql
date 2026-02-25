
  
    

  create  table "modeling_lab"."public"."dim_city__dbt_tmp"
  
  
    as
  
  (
    with cities as (
    select distinct
        geolocation_city as city_name,
        geolocation_state as state_code
    from "modeling_lab"."public"."stg_olist__geolocation"
),

final as (
    select
        md5(cast(coalesce(cast(city_name as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(state_code as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as city_pk,
        city_name,
        state_code
    from cities
)

select * from final
  );
  