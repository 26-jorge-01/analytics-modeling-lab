/*
    Simple date dimension generation.
    In a real project, we suggest using dbt_utils.date_spine or a static CSV.
*/

with date_series as (
    select generate_series(
        '2016-01-01'::date,
        '2019-12-31'::date,
        '1 day'::interval
    )::date as date_day
),

final as (
    select
        date_day as date_key,
        date_day as full_date,
        extract(year from date_day) as year,
        extract(month from date_day) as month,
        extract(day from date_day) as day,
        extract(dow from date_day) as day_of_week,
        to_char(date_day, 'Month') as month_name,
        to_char(date_day, 'Day') as day_name,
        case when extract(dow from date_day) in (0, 6) then true else false end as is_weekend
    from date_series
)

select * from final
