import unittest
import os
import networkx as nx
from src.storage.db import init_db, save_snapshot, get_snapshots, get_snapshot_by_id
from src.storage.diff_engine import TopologyDiffEngine
from src.reporting.pdf_generator import PDFIncidentReportGenerator

class TestPersistenceAndReporting(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_aerodrift.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
        self.g1 = nx.DiGraph()
        self.g1.add_node("A", type="VPC")
        self.g1.add_node("B", type="EC2")
        self.g1.add_edge("A", "B", relation="HOSTS")
        
        self.g2 = nx.DiGraph()
        self.g2.add_node("A", type="VPC")
        self.g2.add_node("B", type="EC2")
        self.g2.add_node("0.0.0.0/0", type="Internet")
        self.g2.add_edge("A", "B", relation="HOSTS")
        self.g2.add_edge("0.0.0.0/0", "B", relation="ALLOWS_TRAFFIC", port=5432)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_snapshot_persistence_and_diff(self):
        s1 = save_snapshot("Baseline", self.g1, is_drifted=False, db_path=self.test_db)
        s2 = save_snapshot("Compromised", self.g2, is_drifted=True, db_path=self.test_db)
        
        snaps = get_snapshots(db_path=self.test_db)
        self.assertEqual(len(snaps), 2)
        
        diff = TopologyDiffEngine.diff(s1, s2, db_path=self.test_db)
        self.assertEqual(len(diff.added_nodes), 1)
        self.assertEqual(diff.added_nodes[0]["id"], "0.0.0.0/0")
        self.assertEqual(len(diff.added_edges), 1)

    def test_pdf_report_generation(self):
        gen = PDFIncidentReportGenerator(output_dir="reports")
        report_file = gen.generate_report(
            incident_id="TEST-001",
            target="Database-Server-1",
            path=["0.0.0.0/0", "sg-0002", "Database-Server-1"],
            latency_ms=1.45,
            ast_code="def remediate(): pass",
            audit_log=["Validation passed", "Executed rollback"]
        )
        self.assertTrue(os.path.exists(report_file))

if __name__ == "__main__":
    unittest.main()

