with source as (
    select * from {{ ref('int_secop__standardized') }}
),

ranked as (
    select
        documento_proveedor,
        proveedor_adjudicado,
        tipodocproveedor,
        es_pyme,
        tama_o_mipyme,
        row_number() over (
            partition by documento_proveedor 
            order by count(*) desc, max(ultima_actualizacion) desc
        ) as rank
    from source
    where documento_proveedor is not null
    group by 
        documento_proveedor, proveedor_adjudicado, 
        tipodocproveedor, es_pyme, tama_o_mipyme
),

vendors as (
    select
        {{ dbt_utils.generate_surrogate_key(['documento_proveedor']) }} as vendor_key,
        documento_proveedor,
        proveedor_adjudicado,
        tipodocproveedor,
        es_pyme,
        tama_o_mipyme
    from ranked
    where rank = 1
)

select * from vendors
