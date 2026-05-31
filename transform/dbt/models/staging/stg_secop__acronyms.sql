{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'agency_acronyms') }}
),

renamed as (
    select
        lower(trim(acronym)) as acronym,
        lower(trim(expanded_name)) as expanded_name
    from source
)

select * from renamed
