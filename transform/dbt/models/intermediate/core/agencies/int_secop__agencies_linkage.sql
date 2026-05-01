{{ config(materialized='table') }}

with base as (
    select * from {{ ref('int_secop__agencies_base') }}
),

seeds as (
    select raw_nit, canonical_nit
    from {{ ref('stg_secop__agency_overrides') }}
),

-- 1. Identify the "Golden Anchors". 
-- Within each Smart Blocking Key, the agency with the most contracts is the Anchor.
anchors as (
    select * from (
        select 
            raw_nit as anchor_nit,
            smart_blocking_key,
            clean_name_for_sim as anchor_clean_name,
            raw_name as anchor_raw_name,
            row_number() over (
                partition by smart_blocking_key 
                order by num_contracts desc, length(raw_name) asc, ultima_actualizacion desc
            ) as anchor_rank
        from base
    )
    where anchor_rank = 1
),

-- 2. Compare every agency against the Anchor of its Smart Blocking Key
comparisons as (
    select 
        b.raw_nit,
        b.raw_name,
        b.base_nit,
        b.smart_blocking_key,
        a.anchor_nit,
        a.anchor_raw_name,
        similarity(b.clean_name_for_sim, a.anchor_clean_name) as sim_score
    from base b
    join anchors a on b.smart_blocking_key = a.smart_blocking_key
)

-- 3. Resolve the Canonical NIT using the MDM Waterfall Rules
select
    c.raw_nit,
    c.raw_name,
    c.base_nit,
    c.smart_blocking_key,
    c.sim_score as algorithm_confidence,
    c.anchor_nit as compared_against_anchor,
    c.anchor_raw_name as compared_against_name,
    
    -- ER Waterfall Logic
    case 
        when seed.canonical_nit is not null then 'TIER 1: SEED OVERRIDE'
        when c.raw_nit = c.anchor_nit then 'TIER 2: IS THE ANCHOR'
        when c.sim_score >= 0.60 then 'TIER 3: MATCHED TO ANCHOR'
        else 'TIER 4: ISOLATED (FAILED MATCH)'
    end as linkage_tier,

    COALESCE(
        seed.canonical_nit, -- Manual Override wins
        case 
            when c.sim_score >= 0.60 then c.anchor_nit -- Merges with Anchor
            else c.raw_nit                             -- Isolates as itself
        end
    ) as canonical_nit

from comparisons c
left join seeds seed on c.raw_nit = seed.raw_nit
