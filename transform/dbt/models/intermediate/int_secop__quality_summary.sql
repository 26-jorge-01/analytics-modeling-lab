with base as (
    select contract_fingerprint as record_id from {{ ref('int_secop__standardized') }}
),

issue_aggregation as (
    select
        record_id,
        count(*) as issue_count,
        count(case when severity = 'Critical' then 1 end) as critical_issue_count,
        count(case when severity = 'High' then 1 end) as high_issue_count,
        count(case when severity = 'Medium' then 1 end) as medium_issue_count,
        count(case when rule_id = 'REC_001' then 1 end) as recoverable_flag_count,
        count(case when rule_id = 'TEST_001' then 1 end) as test_flag_count,
        count(case when dimension = 'Risk' then 1 end) as risk_issue_count,
        -- Calculate a raw risk score
        sum(case 
            when rule_id = 'RISK_001' then 50 -- High value
            when rule_id = 'RISK_002' then 10 -- Zero value active
            when severity = 'Critical' then 20
            else 5
        end) as risk_points
    from {{ ref('int_secop__quality_issues') }}
    group by 1
),

final as (
    select
        b.record_id,
        coalesce(agg.issue_count, 0) as issue_count,
        coalesce(agg.critical_issue_count, 0) as critical_issue_count,
        
        -- Quality Score: 100 base, penalty for issues
        greatest(0, 100 
            - (coalesce(agg.critical_issue_count, 0) * 50) 
            - (coalesce(agg.high_issue_count, 0) * 20)
            - (coalesce(agg.medium_issue_count, 0) * 5)
        ) as quality_score,

        coalesce(agg.risk_points, 0) as risk_score,

        case when coalesce(agg.critical_issue_count, 0) = 0 then true else false end as is_valid,
        case when coalesce(agg.recoverable_flag_count, 0) > 0 then true else false end as is_recoverable,
        case when coalesce(agg.test_flag_count, 0) > 0 then true else false end as is_test,
        case 
            when coalesce(agg.risk_issue_count, 0) > 0 
            or coalesce(agg.risk_points, 0) >= 50 then true 
            else false 
        end as is_high_risk,

        case 
            when coalesce(agg.critical_issue_count, 0) > 0 
            or coalesce(agg.high_issue_count, 0) > 0
            or coalesce(agg.risk_issue_count, 0) > 0
            then true 
            else false 
        end as requires_manual_review

    from base b
    left join issue_aggregation agg on b.record_id = agg.record_id
)

select * from final
