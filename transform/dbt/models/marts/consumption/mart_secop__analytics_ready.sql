{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['contract_fingerprint'], 'type': 'hash'},
            {'columns': ['estado_contrato']},
            {'columns': ['fecha_referencia']}
        ]
    )
}}

with base as (
    select * from {{ ref('int_secop__standardized') }}
),

summary as (
    select * from {{ ref('int_secop__quality_summary') }}
),

final as (
    select
        b.*,
        s.quality_score,
        s.risk_score,
        s.is_high_risk,
        case 
            when s.quality_score >= 90
            and b.valor_del_contrato > 0
            and s.is_high_risk = false
            then true 
            else false 
        end as is_ai_ready
    from base b
    inner join summary s on b.contract_fingerprint = s.record_id
    where s.is_valid = true
      and s.is_test = false
      and b.estado_contrato not in ('borrador', 'cancelado')
)

select * from final
