import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = "aerodrift_history.db"

def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Initializes SQLite database and creates the topology_snapshots table."""
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topology_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                label TEXT NOT NULL,
                node_count INTEGER NOT NULL,
                edge_count INTEGER NOT NULL,
                graph_data TEXT NOT NULL,
                is_drifted INTEGER NOT NULL,
                metadata TEXT
            );
        """)
    return conn


def serialize_graph(graph) -> str:
    """Serializes NetworkX graph nodes and edges to a JSON string."""
    nodes = [{"id": n, **data} for n, data in graph.nodes(data=True)]
    edges = [{"source": u, "target": v, **data} for u, v, data in graph.edges(data=True)]
    return json.dumps({"nodes": nodes, "edges": edges})

def deserialize_graph(graph_json: str):
    """Deserializes JSON string into node and edge structures."""
    return json.loads(graph_json)

