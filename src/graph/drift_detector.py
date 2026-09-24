import networkx as nx
import logging

logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self, topology_graph):
        self.graph = topology_graph.graph
