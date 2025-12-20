"""Co-occurrence graph utilities for Risk Analytics.

Builds a simple bipartite co-occurrence graph between:
- actor_id (convention-based identifier)
- source_hash (stable hash of source + content)

This is intentionally lightweight and SQLite-friendly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func


@dataclass(frozen=True)
class GraphNode:
    id: str
    label: str
    type: str  # "actor" | "source_hash"


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    weight: int


def _node_id_actor(actor_id: str) -> str:
    return f"actor:{actor_id}"


def _node_id_source_hash(source_hash: str) -> str:
    return f"hash:{source_hash}"


def build_actor_sourcehash_graph(
    *,
    session,
    ContentEventDB,
    max_edges: int = 300,
    max_nodes: int = 250,
) -> Dict[str, Any]:
    """Build a bipartite co-occurrence graph from content_events.

    Args:
        session: SQLAlchemy session.
        ContentEventDB: ORM model.
        max_edges: Cap on number of edges returned (sorted by weight desc).
        max_nodes: Cap on number of nodes returned.

    Returns:
        A dict with keys: nodes, edges, meta.
    """

    # Group by (actor_id, source_hash) and count co-occurrences.
    rows: List[Tuple[Optional[str], Optional[str], int]] = (
        session.query(
            ContentEventDB.actor_id,
            ContentEventDB.source_hash,
            func.count(ContentEventDB.id),
        )
        .filter(ContentEventDB.actor_id.isnot(None))
        .filter(ContentEventDB.source_hash.isnot(None))
        .group_by(ContentEventDB.actor_id, ContentEventDB.source_hash)
        .order_by(func.count(ContentEventDB.id).desc())
        .limit(max_edges)
        .all()
    )

    nodes: Dict[str, GraphNode] = {}
    edges: List[GraphEdge] = []

    for actor_id, source_hash, count in rows:
        if not actor_id or not source_hash:
            continue

        actor_node_id = _node_id_actor(actor_id)
        hash_node_id = _node_id_source_hash(source_hash)

        if actor_node_id not in nodes:
            if len(nodes) >= max_nodes:
                break
            nodes[actor_node_id] = GraphNode(
                id=actor_node_id,
                label=actor_id,
                type="actor",
            )

        if hash_node_id not in nodes:
            if len(nodes) >= max_nodes:
                break
            label = source_hash[:12] + "…" if len(source_hash) > 12 else source_hash
            nodes[hash_node_id] = GraphNode(
                id=hash_node_id,
                label=label,
                type="source_hash",
            )

        edges.append(GraphEdge(source=actor_node_id, target=hash_node_id, weight=int(count)))

    return {
        "nodes": [n.__dict__ for n in nodes.values()],
        "edges": [e.__dict__ for e in edges],
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "max_edges": max_edges,
            "max_nodes": max_nodes,
        },
    }
