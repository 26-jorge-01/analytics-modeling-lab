with raw_geo as (
    select
        geolocation_zip_code_prefix as zip_code_prefix,
        geolocation_city as city_name,
        geolocation_state as state_code,
        geolocation_lat as lat,
        geolocation_lng as lng
    from {{ ref('stg_olist__geolocation') }}
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
        {{ dbt_utils.generate_surrogate_key(['city_name', 'state_code']) }} as city_pk,
        lat,
        lng
    from agg_geo
)

select * from final
