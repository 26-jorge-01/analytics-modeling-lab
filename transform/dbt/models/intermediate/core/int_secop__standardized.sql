with staging as (
    select * from {{ ref('stg_secop__contracts_api') }}
),

cleaned as (
    select
        /* 
        1. Primary Identity Field
        Generating the fingerprint based on original IDs to identify row-level variations.
        */
        {{ dbt_utils.generate_surrogate_key([
            'id_contrato', 
            'proceso_de_compra', 
            'nit_entidad', 
            'documento_proveedor', 
            'codigo_entidad'
        ]) }} as contract_fingerprint,

        /* 
        2. Dynamic Field Standardization
        Iterating over all columns. String fields are lowercased and unaccented, 
        EXCEPT for technical IDs and URLs which are preserved to maintain linking capability.
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
            {%- if col.column|lower not in exempt_fields -%}
                {%- if col.dtype == 'text' -%}
                    {{ std_string(col.column) }} as {{ col.column }}
                {%- else -%}
                    {{ col.column }}
                {%- endif -%}
            {%- else -%}
                {{ col.column }}
            {%- endif -%}
            {%- if not loop.last %},{% endif %}
        {% endfor %}

    from staging
)

select * from cleaned
