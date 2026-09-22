import asyncio
import logging
from src.ingestion.aws_mock_client import AsyncMockAWSClient
from src.graph.topology_builder import CloudTopologyGraph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AeroDrift")

async def run_week_1():
    logger.info("--- AeroDrift: Week 1 Implementation ---")
    
    client = AsyncMockAWSClient()
    aws_state = await client.get_full_state()
    
    topology = CloudTopologyGraph()
    graph = topology.build_from_aws_state(aws_state)
    
    summary = topology.get_summary()
    logger.info("Topology Summary:")
    for key, val in summary.items():
        logger.info(f"  {key}: {val}")
        
    logger.info("Week 1 implementation successfully executed!")

if __name__ == "__main__":
    asyncio.run(run_week_1())

