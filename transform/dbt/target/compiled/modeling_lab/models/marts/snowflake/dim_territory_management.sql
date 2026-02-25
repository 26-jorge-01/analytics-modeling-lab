with geography as (
    select * from "modeling_lab"."public"."dim_geography"
),

cities as (
    select * from "modeling_lab"."public"."dim_city"
),

states as (
    select * from "modeling_lab"."public"."dim_state"
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
    from geography g
    left join cities c on g.city_pk = c.city_pk
    left join states s on c.state_code = s.state_code
)

select * from final