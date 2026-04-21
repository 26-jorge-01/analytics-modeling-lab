import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://demo:demo@localhost:15432/modeling_lab")

with engine.connect() as conn:
    res = conn.execute(text('SELECT source, count(*) FROM "raw"."secop_contracts" GROUP BY 1')).fetchall()
    print("COUNTS:")
    for r in res:
        print(f"  {r[0]}: {r[1]}")
    
    # Check 2024 specifically
    res = conn.execute(text("SELECT count(*) FROM raw.secop_contracts WHERE source = 'SECOP II' AND (fecha_de_firma >= '2024-01-01' AND fecha_de_firma <= '2024-12-31')")).scalar()
    print(f"SECOP II (2024) Rows: {res}")
