with source as (
    select * from {{ source('raw', 'location_homologation') }}
),

final as (
    select
        lower(trim(raw_location_name)) as raw_location_name,
        lower(trim(target_location_name)) as target_location_name,
        notes
    from source
)

select * from final
