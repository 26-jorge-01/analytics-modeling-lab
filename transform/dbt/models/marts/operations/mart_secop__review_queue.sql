{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['is_recoverable']},
            {'columns': ['is_high_risk']}
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
    /* 
    Records prioritized for manual review or technical enrichment:
    - Recoverable records (Missing NIT but has Name).
    - High Risk alerts.
    - Missing internal business codes.
    */
    select
        b.*,
        s.quality_score,
        s.risk_score,
        s.is_recoverable,
        s.is_high_risk
    from base b
    inner join summary s on b.contract_fingerprint = s.record_id
    where s.requires_manual_review = true
       or s.is_recoverable = true
)

select * from final
