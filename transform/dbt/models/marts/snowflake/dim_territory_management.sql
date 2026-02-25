with geography as (
    select * from {{ ref('dim_geography') }}
),

cities as (
    select * from {{ ref('dim_city') }}
),

states as (
    select * from {{ ref('dim_state') }}
),

final as (
    select
        g.zip_code_prefix,
        c.city_name,
        s.state_code,
        s.region_name,
        s.region_manager,
        s.state_tax_rate,
        g.lat,
        g.lng
    from geography as g
    left join cities as c on g.city_pk = c.city_pk
    left join states as s on c.state_code = s.state_code
)

select * from final
