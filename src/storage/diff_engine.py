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

