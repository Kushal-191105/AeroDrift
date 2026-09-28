import asyncio
import logging
import time
from src.ingestion.aws_mock_client import AsyncMockAWSClient
from src.graph.topology_builder import CloudTopologyGraph
from src.graph.drift_detector import DriftDetector
from src.ui.dashboard import TopologyDashboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AeroDrift")

async def run_week_2():
    logger.info("--- AeroDrift: Week 2 Execution ---")
    
    dashboard = TopologyDashboard()
    client = AsyncMockAWSClient()
    
    # Phase 1: Baseline
    logger.info("Phase 1: Establishing Secure Baseline")
    aws_state = await client.get_full_state()
    
    topology = CloudTopologyGraph()
    topology.build_from_aws_state(aws_state)
    
    # Render UI
    dashboard.render_tree(aws_state)
    
    # Check Drift
    detector = DriftDetector(topology)
    exposures = detector.detect_exposure()
    dashboard.render_drift_alert(exposures)
    
    # Phase 2: Configuration Drift Simulation
    logger.info("Phase 2: Simulating configuration drift...")
    time.sleep(2)
    client.inject_drift()
    
    # Phase 3: Drift Detection
    logger.info("Phase 3: Polling drifted state...")
    drifted_state = await client.get_full_state()
    
    drifted_topology = CloudTopologyGraph()
    drifted_topology.build_from_aws_state(drifted_state)
    
    drifted_detector = DriftDetector(drifted_topology)
    new_exposures = drifted_detector.detect_exposure()
    
    # Render final alert
    dashboard.render_drift_alert(new_exposures)
    
    logger.info("Week 2 implementation successfully executed!")

if __name__ == "__main__":
    asyncio.run(run_week_2())

