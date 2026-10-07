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


    def detect_exposure(self, source_node="0.0.0.0/0", target_type="Database"):
        logger.info(f"Scanning for configuration drift: Direct exposure paths from {source_node} to {target_type}...")
        targets = self._isolate_target_nodes(target_type)
        exposures = []
        
        for target in targets:
            for pred in self.graph.predecessors(target):
                if self.graph.has_edge(source_node, pred):
                    edge_data = self.graph.get_edge_data(source_node, pred)
                    port = edge_data.get("port", 5432)
                    path = [source_node, pred, target]
                    exposures.append({
                        "target": target,
                        "path": path,
                        "sg": pred,
                        "port": port
                    })
                
        return exposures

