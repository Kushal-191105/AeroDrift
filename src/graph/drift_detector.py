import networkx as nx
import logging

logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self, topology_graph):
        self.graph = topology_graph.graph

    def _isolate_target_nodes(self, target_type):
        target_nodes = []
        for n, d in self.graph.nodes(data=True):
            tags = d.get("metadata", {}).get("Tags", [])
            for tag in tags:
                if tag.get("Key") == "Name" and target_type.lower() in tag.get("Value", "").lower():
                    target_nodes.append(n)
        return target_nodes

