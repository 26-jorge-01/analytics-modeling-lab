import requests
import pandas as pd
import json

def get_count(ds_id, where=None):
    url = f"https://www.datos.gov.co/resource/{ds_id}.json?$select=count(*)"
    if where:
        url += f"&$where={where}"
    try:
        r = requests.get(url, timeout=30)
        return int(r.json()[0]['count'])
    except Exception as e:
        return f"Error: {e}"

def investigate_pk_collisions(ds_id, limit=20000):
    url = f"https://www.datos.gov.co/resource/{ds_id}.json?$limit={limit}&$select=*"
    try:
        r = requests.get(url, timeout=60)
        data = r.json()
        df = pd.DataFrame(data)
        
        # Mappings for SECOP II (jbjy-vk9h)
        # PK Cols: ["id_contrato", "proceso_de_compra", "documento_proveedor", "codigo_entidad", "ultima_actualizacion"]
        pk_cols = ["id_contrato", "proceso_de_compra", "documento_proveedor", "codigo_entidad", "ultima_actualizacion"]
        # Check if they exist in df
        present_cols = [c for c in pk_cols if c in df.columns]
        
        if len(present_cols) > 0:
            total_rows = len(df)
            unique_rows = len(df.drop_duplicates(subset=present_cols))
            unique_ids = len(df[':id'].unique()) if ':id' in df.columns else "N/A"
            
            return {
                "total": total_rows,
                "unique_pk": unique_rows,
                "unique_socrata_id": unique_ids,
                "collisions": total_rows - unique_rows
            }
        return "Columns missing"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("--- SECOP II (jbjy-vk9h) ---")
    print(f"Total API rows: {get_count('jbjy-vk9h')}")
    print(f"PK Collision Check: {investigate_pk_collisions('jbjy-vk9h')}")
    
    print("\n--- SECOP I (f789-7hwg) ---")
    print(f"Total API rows (Raw): {get_count('f789-7hwg')}")
    print(f"Total API rows (ADJUDICADO): {get_count('f789-7hwg', where='upper(estado_del_proceso) = \'ADJUDICADO\'')}")
    print(f"PK Collision Check: {investigate_pk_collisions('f789-7hwg')}")
