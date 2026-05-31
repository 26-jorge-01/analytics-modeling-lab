-- ============================================================================
-- Agency Entity Resolution — Complete Metrics Report
-- Run this after `dbt build` to get all headline numbers for your portfolio.
-- ============================================================================

-- 1. BEFORE & AFTER: Entity Counts
-- ============================================================================
with entity_counts as (
    select
        (select count(distinct concat(nit_entidad, '|', nombre_entidad, '|', coalesce(departamento, '')))
         from int_secop__standardized
         where nit_entidad is not null) as raw_distinct_entries,

        (select count(*) from int_secop__agencies_base) as base_entries,

        (select count(distinct canonical_nit) from int_secop__agencies_linkage) as canonical_agencies,

        (select count(*) from int_secop__agencies) as golden_agencies
)
select
    raw_distinct_entries,
    base_entries,
    canonical_agencies,
    golden_agencies,
    round(base_entries::numeric / nullif(golden_agencies, 0), 2) as dedup_ratio,
    round((1 - golden_agencies::numeric / nullif(base_entries, 0)) * 100, 1) as compression_pct
from entity_counts;

-- 2. AUTOMATED MATCH RATE (Tier Distribution)
-- ============================================================================
select
    'AUTOMATED MATCH RATE' as metric,
    round(
        sum(case when linkage_tier in ('TIER 2: IS THE ANCHOR', 'TIER 3: MATCHED TO ANCHOR') then 1 else 0 end)::numeric
        * 100.0 / count(*), 2
    ) as pct,
    sum(case when linkage_tier in ('TIER 2: IS THE ANCHOR', 'TIER 3: MATCHED TO ANCHOR') then 1 else 0 end) as numerator,
    count(*) as denominator
from int_secop__agencies_linkage

union all

select
    'NEEDS HUMAN REVIEW',
    round(
        sum(case when linkage_tier = 'TIER 4: ISOLATED (FAILED MATCH)' then 1 else 0 end)::numeric
        * 100.0 / count(*), 2
    ),
    sum(case when linkage_tier = 'TIER 4: ISOLATED (FAILED MATCH)' then 1 else 0 end),
    count(*)
from int_secop__agencies_linkage

union all

select
    'MANUAL OVERRIDE',
    round(
        sum(case when linkage_tier = 'OVERRIDE' then 1 else 0 end)::numeric
        * 100.0 / count(*), 2
    ),
    sum(case when linkage_tier = 'OVERRIDE' then 1 else 0 end),
    count(*)
from int_secop__agencies_linkage

order by metric;

-- 3. TIER DISTRIBUTION BREAKDOWN
-- ============================================================================
select
    linkage_tier,
    count(*) as records,
    round(count(*)::numeric * 100.0 / sum(count(*)) over(), 2) as pct
from int_secop__agencies_linkage
group by linkage_tier
order by records desc;

-- 4. CONFIDENCE DISTRIBUTION (Fuzzy Match Scores)
-- ============================================================================
select
    case
        when algorithm_confidence >= 0.85 then '0.85 - 1.00 (High)'
        when algorithm_confidence >= 0.75 then '0.75 - 0.84 (Medium-High)'
        when algorithm_confidence >= 0.60 then '0.60 - 0.74 (Medium)'
        when algorithm_confidence >= 0.40 then '0.40 - 0.59 (Low)'
        when algorithm_confidence is not null then '< 0.40 (Very Low)'
        else 'No match (null)'
    end as confidence_band,
    count(*) as records,
    round(count(*)::numeric * 100.0 / sum(count(*)) over(), 2) as pct
from int_secop__agencies_linkage
group by 1
order by 1;

-- 5. ANOMALY QUEUE
-- ============================================================================
select
    review_reason,
    linkage_tier,
    count(*) as flagged_records
from audit_secop__agency_gray_areas
group by review_reason, linkage_tier
order by count(*) desc;

-- 6. FALSE POSITIVES vs FALSE NEGATIVES
-- ============================================================================
select
    'POTENTIAL FALSE POSITIVES (Review to Split)' as anomaly_type,
    count(*) as total
from audit_secop__agency_gray_areas
where linkage_tier like '%FALSE POSITIVE%'

union all

select
    'POTENTIAL FALSE NEGATIVES (Review to Merge)',
    count(*)
from audit_secop__agency_gray_areas
where linkage_tier like '%FALSE NEGATIVE%';

-- 7. OVERRIDE USAGE
-- ============================================================================
select
    'Override records' as metric,
    count(*) as value,
    round(count(*)::numeric * 100.0 / (select count(*) from int_secop__agencies_linkage), 2) as pct_of_total
from int_secop__agencies_linkage
where resolution_method = 'OVERRIDE';

-- 8. TOP AGENCIES BY CONTRACTS
-- ============================================================================
select
    golden_name,
    total_contracts,
    departamento
from dim_secop__agencies
order by total_contracts desc
limit 20;

-- 9. CONTRACTS PER AGENCY DISTRIBUTION
-- ============================================================================
select
    case
        when total_contracts >= 10000 then '10,000+'
        when total_contracts >= 1000 then '1,000 - 9,999'
        when total_contracts >= 100 then '100 - 999'
        when total_contracts >= 10 then '10 - 99'
        else '1 - 9'
    end as contract_volume_band,
    count(*) as agencies,
    round(count(*)::numeric * 100.0 / sum(count(*)) over(), 2) as pct
from dim_secop__agencies
group by 1
order by 1;

-- 10. NITs WITH MULTIPLE LOCATIONS (Blocking Key Proof)
-- ============================================================================
select
    'NITs operating in 2+ locations' as metric,
    count(*) as value
from (
    select base_nit
    from int_secop__agencies_base
    group by base_nit
    having count(distinct concat(departamento, '|', ciudad)) > 1
) multi_location;

-- 11. SUBDIVISION TYPE DISTRIBUTION
-- ============================================================================
select
    subdivision_type,
    count(*) as records,
    round(count(*)::numeric * 100.0 / sum(count(*)) over(), 2) as pct
from int_secop__agencies_base
group by subdivision_type
order by records desc;

-- ============================================================================
-- END REPORT
-- ============================================================================
