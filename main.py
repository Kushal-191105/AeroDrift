import asyncio
import logging
import time
from src.ingestion.aws_mock_client import AsyncMockAWSClient
from src.graph.topology_builder import CloudTopologyGraph
from src.graph.drift_detector import DriftDetector
from src.ui.dashboard import TopologyDashboard
from src.remediation.auto_healer import AutoHealer

import sys
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

async def run_week_3():
    logger.info("=== AeroDrift: Autonomous Cloud Topology & Self-Healing Agent ===")
    
    dashboard = TopologyDashboard()
    client = AsyncMockAWSClient()
    
    # 1. Establish Baseline
    logger.info("Phase 1: Establishing Secure Infrastructure Baseline...")
    aws_state = await client.get_full_state()
    topology = CloudTopologyGraph()
    topology.build_from_aws_state(aws_state)
    dashboard.render_tree(aws_state)
    
    detector = DriftDetector(topology)
    exposures = detector.detect_exposure()
    dashboard.render_drift_alert(exposures)
    
    # 2. Inject Simulated Configuration Drift
    logger.info("Phase 2: Simulating Unapproved Cloud Configuration Drift...")
    time.sleep(1.5)
    client.inject_drift()
    
    # 3. Detect Drift
    logger.info("Phase 3: Real-Time Drift Detection Query...")
    drifted_state = await client.get_full_state()
    drifted_topology = CloudTopologyGraph()
    drifted_topology.build_from_aws_state(drifted_state)
    
    drifted_detector = DriftDetector(drifted_topology)
    new_exposures = drifted_detector.detect_exposure()
    dashboard.render_drift_alert(new_exposures)
    
    # 4. Agentic Self-Healing via AST & Sandbox
    if new_exposures:
        logger.info("Phase 4: Synthesizing AST Remediation Code & Executing in Sandbox...")
        healer = AutoHealer(client)
        results = healer.resolve_drift(new_exposures)
        
        for res in results:
            dashboard.render_remediation_preview(res.generated_code)
            dashboard.render_remediation_result(res)
            
        # 5. Post-Remediation Verification
        logger.info("Phase 5: Post-Remediation Verification & Topology Re-Indexing...")
        healed_state = await client.get_full_state()
        healed_topology = CloudTopologyGraph()
        healed_topology.build_from_aws_state(healed_state)
        
        healed_detector = DriftDetector(healed_topology)
        final_exposures = healed_detector.detect_exposure()
        dashboard.render_drift_alert(final_exposures)

if __name__ == "__main__":
    asyncio.run(run_week_3())

