"""
Declarative DAG Workflow Execution Engine for KOSIF Think.
Inspired by Temporal, Prefect, and Airflow.
Executes multi-step parallel & sequential pipelines with cycle detection,
dependency resolution, parameter interpolation, and state checkpoints.
Zero external dependencies. Pure Python.
"""

import asyncio
import time
from typing import Dict, Any, List, Set, Optional, Callable
from collections import defaultdict, deque

class DAGNode:
    """Represents a single executable task within a directed acyclic graph."""

    def __init__(
        self,
        node_id: str,
        lane: str,
        intent: str,
        params: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        retries: int = 2
    ):
        self.node_id = node_id
        self.lane = lane
        self.intent = intent
        self.params = params or {}
        self.dependencies = dependencies or []
        self.retries = retries
        self.status = "pending"  # pending, running, completed, failed
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "lane": self.lane,
            "intent": self.intent,
            "dependencies": self.dependencies,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "error": self.error
        }


class DAGWorkflow:
    """Manages DAG graph topology, cycle validation, and parallel execution."""

    def __init__(self, workflow_id: str, title: str):
        self.workflow_id = workflow_id
        self.title = title
        self.nodes: Dict[str, DAGNode] = {}

    def add_node(self, node: DAGNode) -> "DAGWorkflow":
        """Adds a task node to the workflow."""
        self.nodes[node.node_id] = node
        return self

    def validate_acyclic(self) -> bool:
        """Validates that the graph contains no cycles using Kahn's algorithm."""
        in_degree = {nid: 0 for nid in self.nodes}
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    raise ValueError(f"Dependency '{dep}' referenced by '{node.node_id}' does not exist.")
            in_degree[node.node_id] = len(node.dependencies)

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        visited_count = 0

        # Build reverse adjacency list
        adj = defaultdict(list)
        for nid, node in self.nodes.items():
            for dep in node.dependencies:
                adj[dep].append(nid)

        while queue:
            curr = queue.popleft()
            visited_count += 1
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return visited_count == len(self.nodes)

    def get_execution_stages(self) -> List[List[str]]:
        """Groups node IDs into parallelizable topological execution stages."""
        if not self.validate_acyclic():
            raise ValueError(f"Workflow '{self.workflow_id}' contains cyclic dependencies.")

        # Compute level / depth for each node
        depths = {}

        def get_depth(nid: str, visited: Set[str]) -> int:
            if nid in depths:
                return depths[nid]
            node = self.nodes[nid]
            if not node.dependencies:
                depths[nid] = 0
                return 0
            visited.add(nid)
            max_d = 0
            for dep in node.dependencies:
                d = get_depth(dep, visited.copy())
                if d + 1 > max_d:
                    max_d = d + 1
            depths[nid] = max_d
            return max_d

        for nid in self.nodes:
            get_depth(nid, set())

        stages_map = defaultdict(list)
        for nid, d in depths.items():
            stages_map[d].append(nid)

        return [stages_map[d] for d in sorted(stages_map.keys())]

    async def execute(self, dispatch_fn: Callable[[DAGNode, Dict[str, Any]], Any]) -> Dict[str, Any]:
        """
        Executes the workflow stage by stage.
        Nodes within the same stage run concurrently via asyncio.gather.
        """
        t0 = time.perf_counter()
        stages = self.get_execution_stages()
        context: Dict[str, Any] = {}

        for stage_idx, stage_nodes in enumerate(stages):
            async def run_single_node(nid: str):
                node = self.nodes[nid]
                node.status = "running"
                nt0 = time.perf_counter()
                
                # Interpolate parameters from upstream dependencies
                interpolated_params = dict(node.params)
                for dep in node.dependencies:
                    dep_node = self.nodes[dep]
                    if dep_node.result:
                        interpolated_params[f"dep_{dep}"] = dep_node.result

                attempt = 0
                last_err = None
                while attempt <= node.retries:
                    try:
                        res = await dispatch_fn(node, interpolated_params)
                        node.status = "completed"
                        node.result = res
                        node.duration_ms = round((time.perf_counter() - nt0) * 1000, 2)
                        context[node.node_id] = res
                        return
                    except Exception as ex:
                        last_err = str(ex)
                        attempt += 1
                        if attempt <= node.retries:
                            await asyncio.sleep(0.05 * (2 ** (attempt - 1)))
                
                node.status = "failed"
                node.error = last_err
                node.duration_ms = round((time.perf_counter() - nt0) * 1000, 2)

            await asyncio.gather(*(run_single_node(nid) for nid in stage_nodes))

            # If any node in the stage failed, stop workflow
            failed_in_stage = [nid for nid in stage_nodes if self.nodes[nid].status == "failed"]
            if failed_in_stage:
                break

        total_duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        all_completed = all(n.status == "completed" for n in self.nodes.values())

        return {
            "workflow_id": self.workflow_id,
            "title": self.title,
            "success": all_completed,
            "total_nodes": len(self.nodes),
            "stages_executed": len(stages),
            "duration_ms": total_duration_ms,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()}
        }
