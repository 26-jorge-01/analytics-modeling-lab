{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'agency_overrides') }}
),

renamed as (
    select
        trim(raw_nit_entidad) as raw_nit,
        trim(canonical_nit_entidad) as canonical_nit,
        trim(notes) as override_notes
    from source
)

select * from renamed
