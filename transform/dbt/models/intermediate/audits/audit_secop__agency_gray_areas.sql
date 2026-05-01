{{ config(materialized='view') }}

with linkage as (
    select * from {{ ref('int_secop__agencies_linkage') }}
),

base as (
    select * from {{ ref('int_secop__agencies_base') }}
),

-- Detect cases where the same Base NIT exists in different locations with similar names
cross_city_matches as (
    select 
        b.raw_nit,
        b.raw_name,
        a.anchor_nit,
        a.anchor_raw_name as anchor_name,
        similarity(b.clean_name_for_sim, a.anchor_clean_name) as algorithm_confidence,
        'CROSS-CITY: POTENTIAL MISSING MERGE (Same NIT, Different Location)' as review_reason,
        'POTENTIAL FALSE NEGATIVE (Cross-City)' as linkage_tier,
        concat(b.raw_nit, ',', a.anchor_nit) as suggested_csv_entry
    from base b
    -- Find anchors in OTHER smart_blocking_key buckets that share the same base_nit
    inner join (
        select anchor_nit, smart_blocking_key, base_nit, anchor_clean_name, anchor_raw_name 
        from (
            select 
                raw_nit as anchor_nit, 
                smart_blocking_key, 
                base_nit, 
                clean_name_for_sim as anchor_clean_name,
                raw_name as anchor_raw_name,
                row_number() over (partition by smart_blocking_key order by num_contracts desc) as r
            from base
        ) where r = 1
    ) a on b.base_nit = a.base_nit and b.smart_blocking_key != a.smart_blocking_key
    where similarity(b.clean_name_for_sim, a.anchor_clean_name) >= 0.60
),

-- Detect cases where different NITs have extremely similar names (Typo Detection)
cross_nit_matches as (
    select 
        a.anchor_nit as raw_nit,
        a.anchor_raw_name as raw_name,
        b.anchor_nit as anchor_nit,
        b.anchor_raw_name as anchor_name,
        similarity(a.anchor_clean_name, b.anchor_clean_name) as algorithm_confidence,
        'CROSS-NIT: POTENTIAL DUPLICATE (Different NITs, Highly Similar Names)' as review_reason,
        'POTENTIAL FALSE NEGATIVE (Cross-NIT)' as linkage_tier,
        concat(a.anchor_nit, ',', b.anchor_nit) as suggested_csv_entry
    from (
        -- Get all elected anchors and their profiles
        select 
            l.compared_against_anchor as anchor_nit, 
            l.compared_against_name as anchor_raw_name,
            b.clean_name_for_sim as anchor_clean_name
        from linkage l
        join base b on l.raw_nit = b.raw_nit
        where l.linkage_tier = 'TIER 2: IS THE ANCHOR'
    ) a
    inner join (
        select 
            l.compared_against_anchor as anchor_nit, 
            l.compared_against_name as anchor_raw_name,
            b.clean_name_for_sim as anchor_clean_name
        from linkage l
        join base b on l.raw_nit = b.raw_nit
        where l.linkage_tier = 'TIER 2: IS THE ANCHOR'
    ) b on a.anchor_nit < b.anchor_nit -- Unique pairs
    -- Only compare different base NITs (Cross-City is already handled above)
    where split_part(a.anchor_nit, '-', 1) != split_part(b.anchor_nit, '-', 1)
      and similarity(a.anchor_clean_name, b.anchor_clean_name) >= 0.85
),

final_queue as (
    -- Original Linkage-based Gray Areas
    select
        raw_nit,
        raw_name,
        anchor_nit,
        anchor_name,
        algorithm_confidence,
        review_reason,
        linkage_tier,
        suggested_csv_entry
    from (
        select
            raw_nit,
            raw_name,
            compared_against_anchor as anchor_nit,
            compared_against_name as anchor_name,
            algorithm_confidence,
            
            case 
                when linkage_tier = 'TIER 3: MATCHED TO ANCHOR' and algorithm_confidence < 0.75 
                    then 'POTENTIAL FALSE POSITIVE (Review to Split)'
                    
                when linkage_tier = 'TIER 4: ISOLATED (FAILED MATCH)' and algorithm_confidence >= 0.40 
                    then 'POTENTIAL FALSE NEGATIVE (Review to Merge)'
            end as review_reason,
            linkage_tier,
            
            case
                when linkage_tier = 'TIER 3: MATCHED TO ANCHOR' then concat(raw_nit, ',', raw_nit)
                when linkage_tier = 'TIER 4: ISOLATED (FAILED MATCH)' then concat(raw_nit, ',', compared_against_anchor)
            end as suggested_csv_entry
        from linkage
    ) 
    where review_reason is not null

    union all

    -- New Cross-City potential merges
    select * from cross_city_matches

    union all

    -- New Cross-NIT potential duplicates
    select * from cross_nit_matches
),

deduplicated_queue as (
    select * from (
        select 
            *,
            row_number() over (
                partition by raw_nit 
                order by 
                    case 
                        when review_reason like 'CROSS-NIT%' then 1
                        when review_reason like 'CROSS-CITY%' then 2
                        else 3 
                    end asc,
                    algorithm_confidence desc
            ) as priority_rank
        from final_queue
    ) where priority_rank = 1
)

select * from deduplicated_queue
order by 
    review_reason, 
    case 
        when review_reason like '%NEGATIVE%' then algorithm_confidence 
        else (1 - algorithm_confidence) 
    end desc
