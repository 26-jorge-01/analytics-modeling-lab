with raw_geo as (
    select
        geolocation_zip_code_prefix as zip_code_prefix,
        geolocation_city as city_name,
        geolocation_state as state_code,
        geolocation_lat as lat,
        geolocation_lng as lng
    from "modeling_lab"."public"."stg_olist__geolocation"
),

agg_geo as (
    select
        zip_code_prefix,
        city_name,
        state_code,
        avg(lat) as lat,
        avg(lng) as lng
    from raw_geo
    group by 1, 2, 3
),

final as (
    select
        zip_code_prefix,
        md5(cast(coalesce(cast(city_name as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(state_code as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as city_pk,
        lat,
        lng
    from agg_geo
)

select * from final