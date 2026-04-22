with base as (
    select * from {{ ref('mart_secop__analytics_ready') }}
)

select
    *
from base
where is_ai_ready = true
