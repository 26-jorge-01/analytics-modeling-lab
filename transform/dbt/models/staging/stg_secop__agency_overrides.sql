with source as (
    select * from {{ source('raw', 'agency_overrides') }}
),

renamed as (
    select
        raw_nit_entidad as raw_nit,
        raw_name_entidad as raw_name,
        canonical_nit_entidad as canonical_nit,
        canonical_name,
        override_subdivision_type,
        notes
    from source
)

select * from renamed
