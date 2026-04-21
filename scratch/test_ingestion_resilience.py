import unittest
import pandas as pd
import numpy as np
import hashlib
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import sys
import os

# Add root and ingestion dirs to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "ingestion"))

# Mock the database engine since we don't have Postgres
from sqlalchemy import create_engine, text
mock_engine = create_engine('sqlite:///:memory:')

# Pre-mocking to prevent connection attempts during import
# We use 'main' as RAW_SCHEMA for SQLite compatibility
with patch('load_core.get_engine', return_value=mock_engine):
    with patch('load_core.ensure_schema_exists', return_value=None):
        import ingestion.load_secop_api as load_secop_api
        load_secop_api.get_engine = lambda: mock_engine
        load_secop_api.ensure_schema_exists = lambda e, s: None
        load_secop_api.RAW_SCHEMA = "main" # SQLite default schema
        from ingestion.load_secop_api import MatrixStreamer, sanitize_db_columns

class TestIngestionResilience(unittest.TestCase):
    def setUp(self):
        # Override the MatrixStreamer initialization
        with patch('ingestion.load_secop_api.SecopClient') as MockClient:
            self.streamer = MatrixStreamer(table_name="test_contracts")
            self.streamer.engine = mock_engine
            self.streamer.client = MockClient()
            
        # Ensure clean table for each test
        with mock_engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS test_contracts"))
            conn.execute(text("DROP TABLE IF EXISTS ingestion_metadata"))
            conn.commit()

    def _init_table(self, df):
        """Helper to trigger table creation in the mock DB."""
        # Standardize DF for schema initialization
        df_init = df.copy()
        df_init = sanitize_db_columns(df_init)
        df_init['source'] = 'initialization'
        df_init['ingested_at'] = datetime.now()
        df_init['hash_id'] = 'init'
        self.streamer._ensure_data_table(df_init)

    def test_scenario_a_watermark_bypass(self):
        """
        Verify: If the API returns a record with an old 'ultima_actualizacion' but new content,
        the 'hash_id' must catch it (using Content Hashing).
        """
        df1 = pd.DataFrame([{
            'id_contrato': 'C1',
            'proceso_de_compra': 'P1',
            'nit_entidad': 'N1',
            'documento_proveedor': 'D1',
            'ultima_actualizacion': pd.to_datetime('2023-01-01T00:00:00.000000'),
            'valor_del_contrato': 1000,
            'estado_contrato': 'Activo'
        }])
        
        self._init_table(df1)
        
        from queue import Queue
        self.streamer.queue = Queue()
        self.streamer.queue.put(('SECOP_II', 'scavenger', 0, None, df1))
        self.streamer.queue.put(None)
        self.streamer.writer_worker()
        
        # Verify first record
        with mock_engine.connect() as conn:
            res = conn.execute(text("SELECT count(*) FROM test_contracts")).scalar()
            self.assertEqual(res, 1)

        # Simulate "Bypass": API returns same contract, same timestamp, but NEW value
        df2 = pd.DataFrame([{
            'id_contrato': 'C1',
            'proceso_de_compra': 'P1',
            'nit_entidad': 'N1',
            'documento_proveedor': 'D1',
            'ultima_actualizacion': pd.to_datetime('2023-01-01T00:00:00.000000'),
            'valor_del_contrato': 2000,
            'estado_contrato': 'Cerrado'
        }])
        
        self.streamer.queue = Queue()
        self.streamer.queue.put(('SECOP_II', 'scavenger', 1, None, df2))
        self.streamer.queue.put(None)
        self.streamer.writer_worker()

        with mock_engine.connect() as conn:
            res = conn.execute(text("SELECT count(*) FROM test_contracts")).scalar()
            self.assertEqual(res, 2, "Failed Scenario A: Content change with stale timestamp was not captured!")

    def test_scenario_b_sub_second_precision(self):
        """
        Verify: Microsecond precision prevents collisions in rapid updates.
        """
        t1 = pd.to_datetime("2023-01-01T12:00:00.123456")
        t2 = pd.to_datetime("2023-01-01T12:00:00.123457")
        
        df = pd.DataFrame([
            {
                'id_contrato': 'C2', 'proceso_de_compra': 'P2', 'nit_entidad': 'N2', 
                'documento_proveedor': 'D2', 'ultima_actualizacion': t1, 'val': 1
            },
            {
                'id_contrato': 'C2', 'proceso_de_compra': 'P2', 'nit_entidad': 'N2', 
                'documento_proveedor': 'D2', 'ultima_actualizacion': t2, 'val': 2
            }
        ])
        
        self._init_table(df)
        
        from queue import Queue
        self.streamer.queue = Queue()
        self.streamer.queue.put(('SECOP_II', 'scavenger', 0, None, df))
        self.streamer.queue.put(None)
        self.streamer.writer_worker()
        
        with mock_engine.connect() as conn:
            res = conn.execute(text("SELECT count(*) FROM test_contracts")).scalar()
            self.assertEqual(res, 2, "Failed Scenario B: Microsecond difference caused a collision!")

    def test_scenario_c_reality_selection_logic(self):
        """
        Simulate the dbt logic: Verify that ingested_at handles the "Reality" better 
        than bugged API timestamps.
        """
        df_early = pd.DataFrame([{
            'id_contrato': 'C3', 'proceso_de_compra': 'P3', 'nit_entidad': 'N3', 
            'documento_proveedor': 'D3', 'ultima_actualizacion': pd.to_datetime('2023-10-10T00:00:00'), 'status': 'WRONG'
        }])
        
        self._init_table(df_early)
        
        from queue import Queue
        self.streamer.queue = Queue()
        self.streamer.queue.put(('SECOP_II', 'scavenger', 0, None, df_early))
        self.streamer.queue.put(None)
        self.streamer.writer_worker()
        
        import time
        time.sleep(0.1)
        
        df_correction = pd.DataFrame([{
            'id_contrato': 'C3', 'proceso_de_compra': 'P3', 'nit_entidad': 'N3', 
            'documento_proveedor': 'D3', 'ultima_actualizacion': pd.to_datetime('2023-01-01T00:00:00'), 'status': 'CORRECT'
        }])
        self.streamer.queue = Queue()
        self.streamer.queue.put(('SECOP_II', 'scavenger', 1, None, df_correction))
        self.streamer.queue.put(None)
        self.streamer.writer_worker()
        
        sql = """
            SELECT status FROM (
                SELECT status, row_number() OVER (
                    PARTITION BY id_contrato ORDER BY ingested_at DESC, ultima_actualizacion DESC
                ) as row_num
                FROM test_contracts
            ) t WHERE row_num = 1
        """
        with mock_engine.connect() as conn:
            reality = conn.execute(text(sql)).scalar()
            self.assertEqual(reality, 'CORRECT', "Failed Scenario C: Reality selection prioritized bugged timestamp over ingestion order!")

if __name__ == "__main__":
    unittest.main()
