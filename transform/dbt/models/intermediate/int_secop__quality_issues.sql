with base as (
    select * from {{ ref('int_secop__standardized') }}
),

rules as (
    -- ID_001: Missing NIT
    select
        contract_fingerprint as record_id,
        'ID_001' as rule_id,
        'Missing Entity NIT' as rule_name,
        'Completeness' as dimension,
        'Critical' as severity,
        'nit_entidad' as field_name,
        nit_entidad as observed_value,
        'The NIT (Tax ID) of the entity is missing or empty.' as issue_description,
        current_timestamp as detected_at,
        '1.0' as quality_version
    from base
    where nit_entidad is null or trim(nit_entidad) = ''

    union all

    -- ID_002: Missing Entity Code
    select
        contract_fingerprint,
        'ID_002',
        'Missing Entity Code',
        'Completeness',
        'High',
        'codigo_entidad',
        codigo_entidad,
        'The internal entity code is missing.',
        current_timestamp,
        '1.0'
    from base
    where codigo_entidad is null or trim(codigo_entidad) = ''

    union all

    -- VAL_001: Negative Contract Value
    select
        contract_fingerprint,
        'VAL_001',
        'Negative Contract Value',
        'Validity',
        'Critical',
        'valor_del_contrato',
        cast(valor_del_contrato as text),
        'Contract value cannot be negative.',
        current_timestamp,
        '1.0'
    from base
    where valor_del_contrato < 0

    union all

    -- TEST_001: Explicit Test Records
    select
        contract_fingerprint,
        'TEST_001',
        'Confirmed Test Record',
        'Validity',
        'Critical',
        'objeto_del_contrato',
        objeto_del_contrato,
        'Record identified as a test or non-production entry based on object description.',
        current_timestamp,
        '1.0'
    from base
    where lower(trim(objeto_del_contrato)) in ('prueba', 'test', 'error', 'dummy', 'ejemplo')
       or lower(trim(id_contrato)) in ('prueba', 'test', 'error', 'dummy')

    union all

    -- RISK_001: High Value Contract (Threshold >= 1B COP)
    select
        contract_fingerprint,
        'RISK_001',
        'High Value Alert',
        'Risk',
        'High',
        'valor_del_contrato',
        cast(valor_del_contrato as text),
        'Contract value is 1 Billion COP or higher. Requires careful audit.',
        current_timestamp,
        '1.0'
    from base
    where valor_del_contrato >= 1000000000

    union all

    -- RISK_002: Zero Value Active Contract
    select
        contract_fingerprint,
        'RISK_002',
        'Zero Value Active Contract',
        'Risk',
        'Medium',
        'valor_del_contrato',
        '0',
        'Active or In-Execution contract with zero value. Possible framework agreement or data gap.',
        current_timestamp,
        '1.0'
    from base
    where valor_del_contrato = 0 
      and estado_contrato in ('en ejecucion', 'activo', 'aprobado')

    union all

    -- REC_001: Recoverable Entity Identity
    select
        contract_fingerprint,
        'REC_001',
        'Recoverable Identity',
        'Recoverability',
        'Low',
        'nit_entidad',
        null,
        'NIT is missing but Entity Name exists. Identity could be reconstructed.',
        current_timestamp,
        '1.0'
    from base
    where (nit_entidad is null or trim(nit_entidad) = '')
      and (nombre_entidad is not null and trim(nombre_entidad) <> '' and nombre_entidad <> 'ENTIDAD NO ESPECIFICADA')
)

select * from rules
