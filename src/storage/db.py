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


def save_snapshot(label: str, graph, is_drifted: bool, metadata: Optional[Dict[str, Any]] = None, db_path: str = DB_PATH) -> int:
    """Saves a point-in-time cloud topology snapshot into SQLite."""
    conn = init_db(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()
    graph_json = serialize_graph(graph)
    meta_json = json.dumps(metadata or {})
    
    with conn:
        cursor = conn.execute("""
            INSERT INTO topology_snapshots (timestamp, label, node_count, edge_count, graph_data, is_drifted, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now_iso, label, graph.number_of_nodes(), graph.number_of_edges(), graph_json, 1 if is_drifted else 0, meta_json))
        snapshot_id = cursor.lastrowid
        
    logger.info(f"Saved snapshot #{snapshot_id} ['{label}'] (Nodes: {graph.number_of_nodes()}, Edges: {graph.number_of_edges()})")
    conn.close()
    return snapshot_id


def get_snapshots(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all historical topology snapshots."""
    conn = init_db(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, label, node_count, edge_count, is_drifted, metadata FROM topology_snapshots ORDER BY id ASC")
    rows = cursor.fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results

def get_snapshot_by_id(snapshot_id: int, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves a full snapshot including serialized graph data."""
    conn = init_db(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topology_snapshots WHERE id = ?", (snapshot_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

