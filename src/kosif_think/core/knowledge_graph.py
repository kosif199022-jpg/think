"""
Cognitive Knowledge Graph & GraphRAG Engine for KOSIF Think.
Inspired by Microsoft GraphRAG, Mem0, and Neo4j.
Stores entities, relations, semantic triples (Subject-Predicate-Object),
performs multi-hop pathfinding, ego-graph neighborhood extraction, and Mermaid visualization.
Zero external dependencies. Pure Python.
"""

from typing import Dict, Any, List, Set, Optional, Tuple
from collections import defaultdict, deque
import time

class KGEntity:
    """Represents an entity node in the knowledge graph."""
    def __init__(self, entity_id: str, entity_type: str, name: str, attributes: Optional[Dict[str, Any]] = None):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = name
        self.attributes = attributes or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.entity_id,
            "type": self.entity_type,
            "name": self.name,
            "attributes": self.attributes
        }


class KGRelation:
    """Represents a directed semantic relationship between two entities."""
    def __init__(self, source_id: str, predicate: str, target_id: str, weight: float = 1.0, attributes: Optional[Dict[str, Any]] = None):
        self.source_id = source_id
        self.predicate = predicate
        self.target_id = target_id
        self.weight = weight
        self.attributes = attributes or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source_id,
            "predicate": self.predicate,
            "target": self.target_id,
            "weight": self.weight
        }


class CognitiveKnowledgeGraph:
    """Directed multigraph knowledge store supporting GraphRAG retrieval."""

    def __init__(self):
        self.entities: Dict[str, KGEntity] = {}
        # Outgoing edges: source_id -> [KGRelation]
        self.adjacency: Dict[str, List[KGRelation]] = defaultdict(list)
        # Incoming edges: target_id -> [KGRelation]
        self.reverse_adjacency: Dict[str, List[KGRelation]] = defaultdict(list)

    def add_entity(self, entity_id: str, entity_type: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> KGEntity:
        """Creates or updates an entity node."""
        entity = KGEntity(entity_id, entity_type, name, attributes)
        self.entities[entity_id] = entity
        return entity

    def add_triple(self, source_id: str, predicate: str, target_id: str, weight: float = 1.0) -> KGRelation:
        """Adds a subject-predicate-object semantic relation."""
        # Auto-create entities if they don't exist
        if source_id not in self.entities:
            self.add_entity(source_id, "Concept", source_id)
        if target_id not in self.entities:
            self.add_entity(target_id, "Concept", target_id)

        rel = KGRelation(source_id, predicate, target_id, weight)
        self.adjacency[source_id].append(rel)
        self.reverse_adjacency[target_id].append(rel)
        return rel

    def get_neighborhood(self, entity_id: str, depth: int = 1) -> Dict[str, Any]:
        """
        Extracts an ego-graph around entity_id up to specified depth (k-hop).
        Used by GraphRAG to ground context from connected concepts.
        """
        if entity_id not in self.entities:
            return {"error": f"Entity '{entity_id}' not found in knowledge graph."}

        visited_nodes: Set[str] = {entity_id}
        collected_relations: List[KGRelation] = []
        queue = deque([(entity_id, 0)])

        while queue:
            curr_id, curr_depth = queue.popleft()
            if curr_depth >= depth:
                continue

            for rel in self.adjacency[curr_id]:
                collected_relations.append(rel)
                if rel.target_id not in visited_nodes:
                    visited_nodes.add(rel.target_id)
                    queue.append((rel.target_id, curr_depth + 1))

            for rel in self.reverse_adjacency[curr_id]:
                collected_relations.append(rel)
                if rel.source_id not in visited_nodes:
                    visited_nodes.add(rel.source_id)
                    queue.append((rel.source_id, curr_depth + 1))

        nodes_data = [self.entities[nid].to_dict() for nid in visited_nodes]
        relations_data = [r.to_dict() for r in collected_relations]

        return {
            "root_entity": entity_id,
            "depth": depth,
            "total_nodes": len(nodes_data),
            "total_relations": len(relations_data),
            "nodes": nodes_data,
            "relations": relations_data
        }

    @property
    def triples(self) -> List[Dict[str, Any]]:
        """Returns all semantic triples in the knowledge graph."""
        all_rels = []
        for rel_list in self.adjacency.values():
            for r in rel_list:
                all_rels.append({
                    "subject": r.source_id,
                    "predicate": r.predicate,
                    "object": r.target_id,
                    "weight": r.weight
                })
        return all_rels

    def get_ego_graph(self, entity_id: str, hops: int = 1) -> List[Dict[str, Any]]:
        """Extracts ego-graph relations for the given entity up to hops distance."""
        res = self.get_neighborhood(entity_id, depth=hops)
        if "relations" in res:
            return [{"subject": r["source"], "predicate": r["predicate"], "object": r["target"]} for r in res["relations"]]
        return []

    def find_shortest_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """Finds the shortest directed path between two entities using BFS."""
        if start_id not in self.entities or end_id not in self.entities:
            return None
        if start_id == end_id:
            return [start_id]

        queue = deque([(start_id, [start_id])])
        visited = {start_id}

        while queue:
            curr, path = queue.popleft()
            for rel in self.adjacency[curr]:
                neighbor = rel.target_id
                if neighbor == end_id:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    find_path = find_shortest_path

    def query_triples(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        obj: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries triples matching pattern constraints."""
        results = []
        candidates = self.adjacency[subject] if subject and subject in self.adjacency else [
            r for rels in self.adjacency.values() for r in rels
        ]

        for rel in candidates:
            if subject and rel.source_id != subject:
                continue
            if predicate and rel.predicate.lower() != predicate.lower():
                continue
            if obj and rel.target_id != obj:
                continue
            results.append(rel.to_dict())

        return results

    def to_mermaid(self) -> str:
        """Renders knowledge graph as a Mermaid flowchart diagram."""
        lines = ["flowchart LR"]
        for nid, entity in self.entities.items():
            clean_name = entity.name.replace('"', '')
            lines.append(f'    {nid}["{clean_name} ({entity.entity_type})"]')

        for rels in self.adjacency.values():
            for r in rels:
                lines.append(f'    {r.source_id} -->|{r.predicate}| {r.target_id}')

        return "\n".join(lines)
