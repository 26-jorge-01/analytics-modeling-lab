import pandas as pd
from sqlalchemy import create_engine, text
import json

def inspect_db():
    engine = create_engine("postgresql://demo:demo@localhost:15432/modeling_lab")
    
    # 1. Check counts in raw table
    with engine.connect() as conn:
        print("--- RAW TABLE COUNTS ---")
        counts = conn.execute(text('SELECT source, count(*) FROM raw.secop_contracts GROUP BY 1')).fetchall()
        for row in counts:
            print(f"{row[0]}: {row[1]}")
            
        print("\n--- DUPLICATE BUSINESS KEYS IN RAW ---")
        # Check if same business key has multiple hashes
        dupes = conn.execute(text('''
            SELECT id_contrato, proceso_de_compra, nit_entidad, documento_proveedor, count(*) as versions, array_agg(hash_id) as hashes
            FROM raw.secop_contracts
            WHERE source = 'SECOP I'
            GROUP BY 1,2,3,4
            HAVING count(*) > 1
            LIMIT 2
        ''')).fetchall()
        
        for row in dupes:
            print(f"Contract: {row[0]} | Process: {row[1]}")
            versions_count = row[4]
            hashes = row[5]
            print(f"  Versions: {versions_count}")
            h1, h2 = hashes[0], hashes[1]
            print(f"  Hash 1: {h1}")
            print(f"  Hash 2: {h2}")
            
            # Compare the full rows for these two hashes
            r1 = conn.execute(text('SELECT * FROM raw.secop_contracts WHERE hash_id = :h'), {"h": h1}).fetchone()
            r2 = conn.execute(text('SELECT * FROM raw.secop_contracts WHERE hash_id = :h'), {"h": h2}).fetchone()
            
            if not r1 or not r2:
                print("  Could not find rows for hashes!")
                continue

            d1 = dict(r1._mapping)
            d2 = dict(r2._mapping)
            
            # Find differences
            diffs = {k: (d1[k], d2[k]) for k in d1 if d1[k] != d2[k]}
            # Hide system columns from diff
            diffs = {k: v for k, v in diffs.items() if k not in ['ingested_at', 'hash_id']}
            print(f"  Content Differences: {diffs}")


if __name__ == "__main__":
    inspect_db()
