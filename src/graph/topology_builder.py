import networkx as nx
import logging

logger = logging.getLogger(__name__)

class CloudTopologyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_from_aws_state(self, aws_state: dict):
        logger.info('Building NetworkX graph from ingested AWS data...')

        for vpc in aws_state.get("vpcs", []):
            self.graph.add_node(vpc["VpcId"], type="VPC", metadata=vpc)

