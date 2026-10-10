import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from src.storage.db import get_snapshot_by_id, deserialize_graph

logger = logging.getLogger(__name__)

@dataclass
class TopologyDiffResult:
    snapshot_a_id: int
    snapshot_b_id: int
    label_a: str
    label_b: str
    added_nodes: List[Dict[str, Any]] = field(default_factory=list)
    removed_nodes: List[Dict[str, Any]] = field(default_factory=list)
    added_edges: List[Dict[str, Any]] = field(default_factory=list)
    removed_edges: List[Dict[str, Any]] = field(default_factory=list)
    total_changes: int = 0


class TopologyDiffEngine:
    """Computes structural differences between two historical graph snapshots."""
    
    @staticmethod
    def _diff_nodes(nodes_a: List[Dict[str, Any]], nodes_b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        ids_a = {n["id"]: n for n in nodes_a}
        ids_b = {n["id"]: n for n in nodes_b}
        
        added = [n for nid, n in ids_b.items() if nid not in ids_a]
        removed = [n for nid, n in ids_a.items() if nid not in ids_b]
        return added, removed


    @staticmethod
    def _edge_key(edge: Dict[str, Any]) -> str:
        return f"{edge['source']}->{edge['target']}:{edge.get('relation', '')}:{edge.get('port', '')}"

    @classmethod
    def _diff_edges(cls, edges_a: List[Dict[str, Any]], edges_b: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        map_a = {cls._edge_key(e): e for e in edges_a}
        map_b = {cls._edge_key(e): e for e in edges_b}
        
        added = [e for k, e in map_b.items() if k not in map_a]
        removed = [e for k, e in map_a.items() if k not in map_b]
        return added, removed


    @classmethod
    def diff(cls, snapshot_id_a: int, snapshot_id_b: int, db_path: str = "aerodrift_history.db") -> TopologyDiffResult:
        """Diffs two snapshots by their SQLite database IDs."""
        snap_a = get_snapshot_by_id(snapshot_id_a, db_path)
        snap_b = get_snapshot_by_id(snapshot_id_b, db_path)
        
        if not snap_a or not snap_b:
            raise ValueError(f"One or both snapshots ({snapshot_id_a}, {snapshot_id_b}) not found.")
            
        data_a = deserialize_graph(snap_a["graph_data"])
        data_b = deserialize_graph(snap_b["graph_data"])
        
        added_nodes, removed_nodes = cls._diff_nodes(data_a.get("nodes", []), data_b.get("nodes", []))
        added_edges, removed_edges = cls._diff_edges(data_a.get("edges", []), data_b.get("edges", []))
        
        total = len(added_nodes) + len(removed_nodes) + len(added_edges) + len(removed_edges)
        
        logger.info(f"Diff complete between #{snapshot_id_a} and #{snapshot_id_b}: {total} total changes detected.")
        return TopologyDiffResult(
            snapshot_a_id=snapshot_id_a,
            snapshot_b_id=snapshot_id_b,
            label_a=snap_a["label"],
            label_b=snap_b["label"],
            added_nodes=added_nodes,
            removed_nodes=removed_nodes,
            added_edges=added_edges,
            removed_edges=removed_edges,
            total_changes=total
        )

