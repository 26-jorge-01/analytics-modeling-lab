{{
    config(
        materialized='incremental',
        unique_key='contract_fingerprint',
        on_schema_change='sync_all_columns'
    )
}}

with staging as (
    select 
        *,
        {{ std_string('ciudad') }} as clean_ciudad_key,
        {{ std_string('departamento') }} as clean_dept_key
    from {{ ref('stg_secop__contracts_api') }}
    {% if is_incremental() %}
        where ingested_at >= (select max(ingested_at) from {{ this }}) - interval '3 days'
    {% endif %}
),

homologation as (
    select * from {{ ref('stg_secop__location_homologation') }}
),

cleaned as (
    select
        /* 
        1. Primary Identity Field
        Generating the fingerprint based on original IDs to identify row-level variations.
        */
        {{ dbt_utils.generate_surrogate_key([
            's.id_contrato', 
            's.proceso_de_compra', 
            's.nit_entidad', 
            's.documento_proveedor', 
            's.codigo_entidad'
        ]) }} as contract_fingerprint,

        /* 
        2. Dynamic Field Standardization
        Iterating over all columns. String fields are lowercased and unaccented.
        Geographic fields (ciudad, departamento) are joined against the homologation table.
        */
        {%- set columns = adapter.get_columns_in_relation(ref('stg_secop__contracts_api')) -%}
        {%- set exempt_fields = [
            'id_contrato', 'proceso_de_compra', 'nit_entidad', 'documento_proveedor', 
            'codigo_entidad', 'id_modalidad', 'id_regimen_de_contratacion', 
            'id_sub_unidad_ejecutora', 'id_grupo', 'id_familia', 'id_clase',
            'codigo_proveedor', 'codigo_bpin', 'numero_de_contrato', 
            'numero_de_cuenta', 'urlproceso', 'uid', 'identificaci_n_representante_legal', 
            'contract_fingerprint'
        ] -%}

        {% for col in columns %}
            {%- if col.column|lower == 'ciudad' -%}
                coalesce(h_city.target_location_name, nullif(nullif(s.clean_ciudad_key, 'no definido'), 'no aplica')) as ciudad
            {%- elif col.column|lower == 'departamento' -%}
                coalesce(h_dept.target_location_name, nullif(nullif(s.clean_dept_key, 'no definido'), 'no aplica')) as departamento
            {%- elif col.column|lower not in exempt_fields -%}
                {%- if col.dtype == 'text' -%}
                    {{ std_string('s.' ~ col.column) }} as {{ col.column }}
                {%- else -%}
                    s.{{ col.column }}
                {%- endif -%}
            {%- else -%}
                s.{{ col.column }}
            {%- endif -%}
            {%- if not loop.last %},{% endif %}
        {% endfor %}

    from staging s
    left join homologation h_city on s.clean_ciudad_key = h_city.raw_location_name
    left join homologation h_dept on s.clean_dept_key = h_dept.raw_location_name
)

select * from cleaned
