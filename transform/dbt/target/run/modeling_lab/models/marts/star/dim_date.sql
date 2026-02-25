
  
    

  create  table "modeling_lab"."public"."dim_date__dbt_tmp"
  
  
    as
  
  (
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
        extract(year from date_day) as date_year,
        extract(month from date_day) as date_month,
        extract(day from date_day) as date_day_of_month,
        extract(dow from date_day) as day_of_week,
        to_char(date_day, 'Month') as month_name,
        to_char(date_day, 'Day') as day_name,
        extract(dow from date_day) in (0, 6) as is_weekend
    from date_series
)

select * from final
  );
  