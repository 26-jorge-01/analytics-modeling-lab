
import requests

def get_socrata_count(dataset_id, where=None):
    url = f"https://www.datos.gov.co/resource/{dataset_id}.json"
    params = {"$select": "count(*)"}
    if where:
        params["$where"] = where
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()[0]['count']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return str(e)

# SECOP I and II IDs from pysecop config
s1_id = "f789-7hwg"
s2_id = "jbjy-vk9h"

print("--- ACTUAL API COUNTS (via Socrata) ---")
c1 = get_socrata_count(s1_id)
c1_adj = get_socrata_count(s1_id, "upper(estado_del_proceso) = 'ADJUDICADO'")
print(f"SECOP I Total: {c1}")
print(f"SECOP I Adjudicado: {c1_adj}")

c2 = get_socrata_count(s2_id)
c2_firma = get_socrata_count(s2_id, 'fecha_de_firma is not null')
c2_backfill = get_socrata_count(s2_id, "fecha_de_firma between '2005-01-01T00:00:00' and '2025-12-31T23:59:59'")

print(f"SECOP II Total: {c2}")
print(f"SECOP II with Fecha Firma: {c2_firma}")
print(f"SECOP II 2005-2025 (Fecha Firma): {c2_backfill}")
