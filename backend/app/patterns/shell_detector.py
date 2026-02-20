import networkx as nx
from typing import List, Set
from uuid import uuid4
from app.utils.ring_utils import generate_ring_id
from app.patterns.base_detector import BaseDetector
from app.models.detection import DetectionResult
from app.config import SHELL_MAX_INTERMEDIATE_DEGREE


class ShellDetector(BaseDetector):

    def detect(self, graph: nx.MultiDiGraph) -> List[DetectionResult]:

        results = []
        visited_paths = set()

        for node in graph.nodes():
            paths = self._dfs_paths(graph, node, max_depth=4)

            for path in paths:
                path_tuple = tuple(path)
                if path_tuple in visited_paths:
                    continue

                if self._is_shell_chain(graph, path):
                    visited_paths.add(path_tuple)

                    ring_nodes = set(path)
                    risk_score, evidence = self._compute_risk(graph, path)

                    results.append(
                        DetectionResult(
                            ring_id=generate_ring_id(sorted(list(ring_nodes)), "cycle"),
                            pattern_type="shell_chain",
                            member_accounts=sorted(list(ring_nodes)),
                            risk_score=round(risk_score, 2),
                            evidence=evidence
                        )
                    )

        return results

    # -----------------------------------
    # DFS Path Builder
    # -----------------------------------

    def _dfs_paths(self, graph, start, max_depth):

        stack = [(start, [start])]
        paths = []

        while stack:
            (vertex, path) = stack.pop()

            if len(path) > max_depth:
                continue

            for _, neighbor, _ in graph.out_edges(vertex, data=True):
                if neighbor in path:
                    continue

                new_path = path + [neighbor]

                if len(new_path) >= 4:  # ≥3 hops
                    paths.append(new_path)

                stack.append((neighbor, new_path))

        return paths

    # -----------------------------------
    # Shell Chain Validation
    # -----------------------------------

    def _is_shell_chain(self, graph, path):

        if len(path) < 4:
            return False

        # Intermediate nodes
        intermediates = path[1:-1]

        # Degree constraint
        for node in intermediates:
            if graph.degree(node) > SHELL_MAX_INTERMEDIATE_DEGREE:
                return False

        # Value retention check
        values = []
        timestamps = []

        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]

            if not graph.has_edge(u, v):
                return False

            edges = graph.get_edge_data(u, v)

            # Choose largest transaction (strongest signal)
            max_edge = max(edges.values(), key=lambda e: e["amount"])
            values.append(max_edge["amount"])
            timestamps.append(max_edge["timestamp"])

        if not values:
            return False

        retention_ratio = min(values) / max(values)

        if retention_ratio < 0.7:
            return False

        # Time compression check
        duration_hours = (
            (max(timestamps) - min(timestamps)).total_seconds() / 3600
        )

        if duration_hours > 168:  # 7 days
            return False

        return True

    # -----------------------------------
    # Risk Computation
    # -----------------------------------

    def _compute_risk(self, graph, path):

        values = []
        timestamps = []

        for i in range(len(path) - 1):
            edges = graph.get_edge_data(path[i], path[i + 1])
            max_edge = max(edges.values(), key=lambda e: e["amount"])
            values.append(max_edge["amount"])
            timestamps.append(max_edge["timestamp"])

        total_value = sum(values)

        duration_hours = (
            (max(timestamps) - min(timestamps)).total_seconds() / 3600
        )

        value_score = min(total_value / 15000, 1.0)
        velocity_score = 1.0 if duration_hours <= 24 else max(0, 1 - duration_hours / 168)
        depth_score = min(len(path) / 6, 1.0)

        risk = (
            0.4 * value_score +
            0.4 * velocity_score +
            0.2 * depth_score
        ) * 100

        evidence = {
            "chain_path": path,
            "total_value": round(total_value, 2),
            "duration_hours": round(duration_hours, 2),
            "chain_length": len(path)
        }

        return min(risk, 100), evidence
