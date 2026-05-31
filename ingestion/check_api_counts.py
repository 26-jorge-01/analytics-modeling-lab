
from pysecop import SecopClient, QueryBuilder
import pandas as pd

client = SecopClient()

def get_count(source, where=None):
    qb = QueryBuilder()
    qb.select(["count(*)"])
    if where:
        qb.where_custom(where)
    df = client.fetch(source, qb, content_type="json")
    return df.iloc[0, 0] if not df.empty else 0

print("--- API COUNTS ---")
s1_total = get_count('SECOP_I')
s1_adj = get_count('SECOP_I', "upper(estado_del_proceso) = 'ADJUDICADO'")

print(f"SECOP I (Total): {s1_total}")
print(f"SECOP I (ADJUDICADO): {s1_adj}")

s2_total = get_count('SECOP_II')
s2_backfill = get_count('SECOP_II', "fecha_de_firma between '2005-01-01' and '2025-12-31'")
s2_missing = get_count('SECOP_II', "fecha_de_firma is null")

print(f"SECOP II (Total): {s2_total}")
print(f"SECOP II (2005-2025): {s2_backfill}")
print(f"SECOP II (Missing Fecha Firma): {s2_missing}")
