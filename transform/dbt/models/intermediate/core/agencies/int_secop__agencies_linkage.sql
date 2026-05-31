with base as (
    select * from {{ ref('int_secop__agencies_base') }}
),

anchors as (
    select
        canonical_nit,
        smart_blocking_key,
        raw_nit as anchor_raw_nit,
        raw_name as anchor_raw_name,
        clean_name_for_sim as anchor_clean_name,
        num_contracts,
        row_number() over (
            partition by canonical_nit, smart_blocking_key 
            order by num_contracts desc, ultima_actualizacion desc
        ) as rn
    from base
    where canonical_nit is not null
),

top_anchors as (
    select * from anchors where rn = 1
),

linkage_tier as (
    select
        b.raw_nit,
        b.raw_name,
        b.smart_blocking_key,
        b.subdivision_type,
        -- Priority 1: Use the pre-resolved canonical identity from manual overrides
        -- Priority 2: Fuzzy match with the anchor of the same block
        case
            when b.has_override then b.canonical_nit
            when a.canonical_nit is not null then a.canonical_nit
            else b.canonical_nit
        end as canonical_nit,
        case
            when b.has_override then 'OVERRIDE'
            when a.canonical_nit is not null then 'FUZZY_BLOCK'
            else 'SINGLETON'
        end as resolution_method,
        similarity(b.clean_name_for_sim, a.anchor_clean_name) as sim_score,
        a.anchor_raw_nit as compared_against_anchor,
        a.anchor_raw_name as compared_against_name,
        similarity(b.clean_name_for_sim, a.anchor_clean_name) as algorithm_confidence,
        case
            when b.has_override then 'OVERRIDE'
            when b.raw_nit = a.anchor_raw_nit then 'TIER 2: IS THE ANCHOR'
            when a.canonical_nit is not null then 'TIER 3: MATCHED TO ANCHOR'
            else 'TIER 4: ISOLATED (FAILED MATCH)'
        end as linkage_tier
    from base b
    left join top_anchors a on b.smart_blocking_key = a.smart_blocking_key
        and not b.has_override -- Only fuzzy match if not already overridden
)

select * from linkage_tier
