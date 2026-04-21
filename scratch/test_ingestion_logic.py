import sys
import os

# Add local paths to sys.path to test the modified library
sys.path.insert(0, os.path.abspath('pysecop'))

from pysecop import SecopClient, QueryBuilder
from pysecop.utils.helpers import get_mapped_column

def test_query_builder():
    print("Testing QueryBuilder...")
    qb = QueryBuilder()
    qb.where_custom("ultima_actualizacion >= '2023-01-01'")
    qb.order("ultima_actualizacion", "ASC")
    qb.order("id_contrato", "ASC")
    qb.limit(10)
    
    query = qb.build()
    print(f"Generated Query: {query}")
    assert "order by ultima_actualizacion ASC, id_contrato ASC" in query
    assert "where ultima_actualizacion >= '2023-01-01'" in query
    print("QueryBuilder tests passed.")

def test_client_order_parsing():
    print("\nTesting SecopClient Order Parsing & Mapping...")
    client = SecopClient()
    
    # Mocking the fetch call to inspect the QueryBuilder it sends
    captured_qb = None
    
    def mock_fetch(dataset_key, qb, content_type="json"):
        nonlocal captured_qb
        captured_qb = qb
        import pandas as pd
        return pd.DataFrame() # Return empty to stop execution

    client.fetch = mock_fetch
    
    # Scenario: SECOP I (where id_contrato maps to id_adjudicacion)
    print("Checking SECOP I mapping...")
    client._fetch_and_process_slice(
        dataset_key="SECOP_I", 
        config=None, 
        limit=10, 
        offset=0, 
        resource_type="contracts", 
        order="ultima_actualizacion ASC, id_contrato ASC"
    )
    
    query = captured_qb.build()
    print(f"SECOP I Query: {query}")
    assert "order by ultima_actualizacion ASC, id_adjudicacion ASC" in query
    
    # Scenario: SECOP II (direct mapping)
    print("Checking SECOP II mapping...")
    client._fetch_and_process_slice(
        dataset_key="SECOP_II", 
        config=None,
        limit=10, 
        offset=0, 
        resource_type="contracts", 
        order="ultima_actualizacion ASC, id_contrato ASC"
    )
    query = captured_qb.build()
    print(f"SECOP II Query: {query}")
    assert "order by ultima_actualizacion ASC, id_contrato ASC" in query
    
    print("SecopClient mapping tests passed.")

if __name__ == "__main__":
    try:
        test_query_builder()
        test_client_order_parsing()
        print("\nALL LOGIC TESTS PASSED SUCCESSFULLY.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
