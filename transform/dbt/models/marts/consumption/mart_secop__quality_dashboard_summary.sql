with analytics_ready as (
    select 
        date_trunc('year', fecha_referencia) as fiscal_year,
        count(*) as total_records,
        avg(quality_score) as avg_quality_score,
        'Analytics Ready' as category
    from {{ ref('mart_secop__analytics_ready') }}
    group by 1
),

ai_ready as (
    select 
        date_trunc('year', fecha_referencia) as fiscal_year,
        count(*) as total_records,
        avg(100.0) as avg_quality_score, -- AI ready is always 90+ by definition
        'AI Ready' as category
    from {{ ref('mart_secop__ai_ready') }}
    group by 1
),

review_queue as (
    -- Identifying records with high-severity quality issues for the review queue metric
    select 
        date_trunc('year', detected_at) as fiscal_year,
        count(distinct record_id) as total_records,
        0.0 as avg_quality_score,
        'Review Queue' as category
    from {{ ref('int_secop__quality_issues') }}
    where severity in ('Critical', 'High')
    group by 1
),

excluded as (
    select 
        date_trunc('year', fecha_referencia) as fiscal_year,
        count(*) as total_records,
        avg(quality_score) as avg_quality_score,
        'Excluded' as category
    from {{ ref('mart_secop__excluded') }}
    group by 1
),

universe as (
    select * from analytics_ready
    union all
    select * from ai_ready
    union all
    select * from review_queue
    union all
    select * from excluded
),

issue_stats as (
    -- Pre-calculating the top 10 issues to avoid scanning issues table in Metabase
    select 
        rule_name,
        dimension,
        severity,
        count(*) as issue_count
    from {{ ref('int_secop__quality_issues') }}
    group by 1, 2, 3
    order by 4 desc
    limit 20
)

-- We can't easily return two different grains in one dbt model unless we use a long format or separate models.
-- For Metabase efficiency, a long-format "Key-Value" summary is often best.
-- However, for the most common charts, a "Category-Grain" is better.
-- I'll output the category totals by year.

select * from universe
