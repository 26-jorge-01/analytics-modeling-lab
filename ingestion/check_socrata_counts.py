
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

print("--- ACTUAL API COUNTS (via Socrata) ---")
s1_total = get_socrata_count('79me-wcun')
s1_adj = get_socrata_count('79me-wcun', "upper(estado_del_proceso) = 'ADJUDICADO'")

print(f"SECOP I Total: {s1_total}")
print(f"SECOP I ADJUDICADO: {s1_adj}")

s2_total = get_socrata_count('jbjy-vvct')
s2_with_firma = get_socrata_count('jbjy-vvct', "fecha_de_firma is not null")
s2_without_firma = get_socrata_count('jbjy-vvct', "fecha_de_firma is null")
s2_backfill = get_socrata_count('jbjy-vvct', "fecha_de_firma between '2005-01-01T00:00:00' and '2025-12-31T23:59:59'")

print(f"SECOP II Total: {s2_total}")
print(f"SECOP II with Fecha Firma: {s2_with_firma}")
print(f"SECOP II without Fecha Firma: {s2_without_firma}")
print(f"SECOP II 2005-2025 (Fecha Firma): {s2_backfill}")
