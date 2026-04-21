import sqlalchemy
from sqlalchemy import inspect
from dotenv import load_dotenv
import os

load_dotenv()
db_uri = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}'
engine = sqlalchemy.create_engine(db_uri)

inspector = inspect(engine)
columns = [c["name"] for c in inspector.get_columns("raw_secop_api_contracts", schema="raw")]
pk = inspector.get_pk_constraint("raw_secop_api_contracts", schema="raw")["column_names"]

print(f"--- Schema Verification ---")
print(f"Primary Key: {pk}")
print(f"Contains 'hash_id': {'hash_id' in columns}")
print(f"Contains 'id' (Socrata): {'id' in columns}")
print(f"Contains 'uid': {'uid' in columns}")
print(f"Total Columns: {len(columns)}")

with engine.connect() as conn:
    res = conn.execute(sqlalchemy.text("SELECT count(*) FROM raw.raw_secop_api_contracts")).fetchone()
    print(f"\nTotal Records: {res[0]}")
    
    res_i = conn.execute(sqlalchemy.text("SELECT count(*) FROM raw.raw_secop_api_contracts WHERE source = 'SECOP I'")).fetchone()
    print(f"SECOP I Records: {res_i[0]}")
    
    res_ii = conn.execute(sqlalchemy.text("SELECT count(*) FROM raw.raw_secop_api_contracts WHERE source = 'SECOP II'")).fetchone()
    print(f"SECOP II Records: {res_ii[0]}")
