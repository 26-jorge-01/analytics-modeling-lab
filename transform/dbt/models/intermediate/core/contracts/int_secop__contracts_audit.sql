{{
    config(
        materialized='view',
        schema='intermediate'
    )
}}

WITH contract_versions AS (
    SELECT 
        id_contrato,
        nit_entidad,
        source,
        estado_contrato,
        valor_del_contrato,
        ultima_actualizacion,
        ingested_at,
        hash_id,
        LAG(estado_contrato) OVER (PARTITION BY id_contrato, nit_entidad ORDER BY ingested_at) as prev_status,
        LAG(valor_del_contrato) OVER (PARTITION BY id_contrato, nit_entidad ORDER BY ingested_at) as prev_value,
        LAG(ultima_actualizacion) OVER (PARTITION BY id_contrato, nit_entidad ORDER BY ingested_at) as prev_ua,
        COUNT(*) OVER (PARTITION BY id_contrato, nit_entidad) as version_count
    FROM {{ ref('stg_secop__contracts_api') }}
)

SELECT 
    *,
    CASE 
        WHEN version_count > 1 AND ultima_actualizacion = prev_ua THEN 'SILENT_UPDATE'
        WHEN prev_status = 'Liquidado' AND estado_contrato != 'Liquidado' THEN 'STATUS_REVERSION'
        WHEN prev_value IS NOT NULL AND ABS(valor_del_contrato - prev_value) / NULLIF(prev_value, 0) > 0.5 THEN 'MASSIVE_VALUE_CHANGE'
        ELSE 'NORMAL'
    END as anomaly_type
FROM contract_versions
WHERE version_count > 1
