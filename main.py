import asyncio
import logging
import time
import argparse
import sys

from src.ingestion.aws_mock_client import AsyncMockAWSClient
from src.graph.topology_builder import CloudTopologyGraph
from src.graph.drift_detector import DriftDetector
from src.ui.dashboard import TopologyDashboard
from src.remediation.auto_healer import AutoHealer
from src.storage.db import save_snapshot, get_snapshots
from src.storage.diff_engine import TopologyDiffEngine
from src.reporting.pdf_generator import PDFIncidentReportGenerator

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AeroDrift")

async def run_aerodrift_pipeline():
    logger.info("=== AeroDrift: Autonomous CloudOps Topology, Drift & Self-Healing Agent ===")
    
    dashboard = TopologyDashboard()
    client = AsyncMockAWSClient()
    pdf_gen = PDFIncidentReportGenerator()
    
    # --- PHASE 1: SECURE BASELINE ---
    logger.info("Phase 1: Establishing Secure Infrastructure Baseline...")
    baseline_state = await client.get_full_state()
    baseline_topo = CloudTopologyGraph()
    baseline_topo.build_from_aws_state(baseline_state)
    dashboard.render_tree(baseline_state)
    
    snap1_id = save_snapshot("Baseline-Secure", baseline_topo.graph, is_drifted=False)
    
    detector = DriftDetector(baseline_topo)
    exposures = detector.detect_exposure()
    dashboard.render_drift_alert(exposures)
    
    # --- PHASE 2: INJECT DRIFT ---
    logger.info("Phase 2: Simulating Unapproved Cloud Configuration Drift...")
    time.sleep(1.2)
    client.inject_drift()
    
    # --- PHASE 3: REAL-TIME DETECTION ---
    logger.info("Phase 3: Real-Time Drift Detection Query...")
    drifted_state = await client.get_full_state()
    drifted_topo = CloudTopologyGraph()
    drifted_topo.build_from_aws_state(drifted_state)
    
    snap2_id = save_snapshot("Drifted-State", drifted_topo.graph, is_drifted=True)
    
    drifted_detector = DriftDetector(drifted_topo)
    active_exposures = drifted_detector.detect_exposure()
    dashboard.render_drift_alert(active_exposures)
    
    # Render Topology Diff: Baseline vs Drifted
    diff_1_2 = TopologyDiffEngine.diff(snap1_id, snap2_id)
    dashboard.render_topology_diff(diff_1_2)
    
    # --- PHASE 4: AGENTIC SELF-HEALING (AST + SANDBOX) ---
    if active_exposures:
        logger.info("Phase 4: Synthesizing AST Remediation Code & Executing in Sandbox...")
        healer = AutoHealer(client)
        results = healer.resolve_drift(active_exposures)
        
        for res in results:
            dashboard.render_remediation_preview(res.generated_code)
            dashboard.render_remediation_result(res)
            
            # --- PHASE 5: POST-REMEDIATION VERIFICATION ---
            logger.info("Phase 5: Post-Remediation Verification & Topology Re-Indexing...")
            healed_state = await client.get_full_state()
            healed_topo = CloudTopologyGraph()
            healed_topo.build_from_aws_state(healed_state)
            
            snap3_id = save_snapshot("Remediated-State", healed_topo.graph, is_drifted=False)
            
            healed_detector = DriftDetector(healed_topo)
            final_exposures = healed_detector.detect_exposure()
            dashboard.render_drift_alert(final_exposures)
            
            # Render Topology Diff: Drifted vs Remediated
            diff_2_3 = TopologyDiffEngine.diff(snap2_id, snap3_id)
            dashboard.render_topology_diff(diff_2_3)
            
            # --- PHASE 6: AUTOMATED PDF INCIDENT REPORT ---
            logger.info("Phase 6: Generating Automated PDF Incident Audit Report...")
            target = active_exposures[0].get("target", "Database-Server-1")
            path = active_exposures[0].get("path", [])
            report_path = pdf_gen.generate_report(
                incident_id="INC-8092-AWS",
                target=target,
                path=path,
                latency_ms=res.execution_time_ms,
                ast_code=res.generated_code,
                audit_log=res.audit_log
            )
            dashboard.console.print(f"[bold green]📄 Automated Incident PDF Exported:[/bold green] [cyan]{report_path}[/cyan]\n")

def view_history():
    dashboard = TopologyDashboard()
    snapshots = get_snapshots()
    from rich.table import Table
    table = Table(title="🏛️ Historical Cloud Topology Snapshots (SQLite)", show_header=True)
    table.add_column("ID", justify="center", width=6)
    table.add_column("Timestamp (UTC)", width=28)
    table.add_column("Label", style="cyan", width=20)
    table.add_column("Nodes", justify="right", width=8)
    table.add_column("Edges", justify="right", width=8)
    table.add_column("Drifted?", justify="center", width=10)
    for s in snapshots:
        drift_tag = "[red]YES[/red]" if s["is_drifted"] else "[green]NO[/green]"
        table.add_row(str(s["id"]), s["timestamp"], s["label"], str(s["node_count"]), str(s["edge_count"]), drift_tag)
    dashboard.console.print(table)

def main():
    parser = argparse.ArgumentParser(description="AeroDrift: Agentic Cloud Topology & Remediation Engine")
    parser.add_argument("--history", action="store_true", help="View historical snapshots in SQLite")
    parser.add_argument("--diff", nargs=2, type=int, metavar=("SNAP_A", "SNAP_B"), help="Diff two topology snapshots by ID")
    args = parser.parse_args()
    
    if args.history:
        view_history()
    elif args.diff:
        dashboard = TopologyDashboard()
        diff_res = TopologyDiffEngine.diff(args.diff[0], args.diff[1])
        dashboard.render_topology_diff(diff_res)
    else:
        asyncio.run(run_aerodrift_pipeline())

if __name__ == "__main__":
    main()

