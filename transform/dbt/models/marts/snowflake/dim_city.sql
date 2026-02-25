with cities as (
    select distinct
        geolocation_city as city_name,
        geolocation_state as state_code
    from {{ ref('stg_olist__geolocation') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['city_name', 'state_code']) }} as city_pk,
        city_name,
        state_code
    from cities
)

select * from final
