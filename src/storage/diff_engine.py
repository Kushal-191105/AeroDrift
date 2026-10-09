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

