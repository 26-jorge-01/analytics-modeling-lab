import pandas as pd
from sqlalchemy import create_engine, text

def check_status():
    engine = create_engine("postgresql://demo:demo@localhost:15432/modeling_lab")
    
    with engine.connect() as conn:
        print("--- METADATA ---")
        meta = conn.execute(text("SELECT * FROM raw.ingestion_metadata")).fetchall()
        for m in meta:
            print(m)
            
        print("\n--- RAW COUNTS PER SOURCE ---")
        counts = conn.execute(text("SELECT source, count(*) FROM raw.secop_contracts GROUP BY 1")).fetchall()
        for r in counts:
            print(f"{r[0]}: {r[1]}")

        print("\n--- SAMPLE DUPLICATES IN STAGING ---")
        # Try to run the logic of the staging view manually to see if it deduplicates
        # We'll use the current logic from the .sql file
        dupes = conn.execute(text("""
            WITH ranked AS (
                SELECT id_contrato, proceso_de_compra, nit_entidad, documento_proveedor, source,
                ROW_NUMBER() OVER (
                    PARTITION BY 
                        UPPER(TRIM(CAST(id_contrato AS TEXT))), 
                        UPPER(TRIM(CAST(proceso_de_compra AS TEXT))), 
                        UPPER(TRIM(CAST(nit_entidad AS TEXT))), 
                        UPPER(TRIM(CAST(documento_proveedor AS TEXT))),
                        source
                    ORDER BY ingested_at DESC
                ) as row_num
                FROM raw.secop_contracts
                WHERE source = 'SECOP I'
            )
            SELECT row_num, count(*) FROM ranked GROUP BY 1 ORDER BY 1;
        """)).fetchall()
        for d in dupes:
            print(f"Row Num {d[0]}: {d[1]}")

if __name__ == "__main__":
    check_status()
