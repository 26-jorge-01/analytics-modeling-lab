with base as (
    select * from {{ ref('int_secop__standardized') }}
),

summary as (
    select * from {{ ref('int_secop__quality_summary') }}
),

final as (
    /* 
    Records excluded from production use:
    - Confirmed test records.
    - Terminal states that represent non-contracted or canceled efforts.
    - Non-recoverable critical failures.
    */
    select
        b.*,
        s.quality_score,
        s.risk_score
    from base b
    inner join summary s on b.contract_fingerprint = s.record_id
    where s.is_test = true
       or b.estado_contrato in ('borrador', 'cancelado')
)

select * from final
