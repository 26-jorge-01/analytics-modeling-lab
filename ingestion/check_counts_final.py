
import requests

def get_socrata_count(dataset_url, where=None):
    params = {"$select": "count(*)"}
    if where:
        params["$where"] = where
    
    try:
        response = requests.get(dataset_url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()[0]['count']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return str(e)

# SECOP I and II URLs from Socrata
s1_url = "https://www.datos.gov.co/resource/79me-wcun.json"
s2_url = "https://www.datos.gov.co/resource/jbjy-vvct.json"

print("--- SECOP API COUNTS ---")
c1 = get_socrata_count(s1_url)
c1_adj = get_socrata_count(s1_url, "upper(estado_del_proceso) = 'ADJUDICADO'")
print(f"SECOP I Total: {c1}")
print(f"SECOP I Adjudicado: {c1_adj}")

c2 = get_socrata_count(s2_url)
c2_firma = get_socrata_count(s2_url, 'fecha_de_firma is not null')
c2_inicio = get_socrata_count(s2_url, 'fecha_de_inicio_del_contrato is not null')
c2_cargue = get_socrata_count(s2_url, 'fecha_de_cargue_en_el_secop is not null')

print(f"SECOP II Total: {c2}")
print(f"SECOP II w/ Fecha Firma: {c2_firma}")
print(f"SECOP II w/ Fecha Inicio: {c2_inicio}")
print(f"SECOP II w/ Fecha Cargue: {c2_cargue}")
