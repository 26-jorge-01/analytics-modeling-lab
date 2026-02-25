with states as (
    select distinct
        geolocation_state as state_code
    from {{ ref('stg_olist__geolocation') }}
),

enriched as (
    select
        state_code,
        case
            when state_code in ('SP', 'RJ', 'ES', 'MG') then 'Southeast'
            when state_code in ('PR', 'SC', 'RS') then 'South'
            when state_code in ('MT', 'MS', 'GO', 'DF') then 'Central-West'
            when state_code in ('BA', 'AL', 'SE', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA') then 'Northeast'
            else 'North'
        end as region_name,
        -- Synthetic Region Manager for business use case demo
        case
            when state_code in ('SP', 'RJ', 'ES', 'MG') then 'Ana Silva'
            when state_code in ('PR', 'SC', 'RS') then 'Bruno Costa'
            when state_code in ('MT', 'MS', 'GO', 'DF') then 'Carlos Oliveira'
            when state_code in ('BA', 'AL', 'SE', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA') then 'Daniela Santos'
            else 'Eduardo Lima'
        end as region_manager,
        -- Synthetic Tax Rate
        case
            when state_code = 'SP' then 0.18
            when state_code = 'RJ' then 0.12
            else 0.10
        end as state_tax_rate
    from states
)

select * from enriched
