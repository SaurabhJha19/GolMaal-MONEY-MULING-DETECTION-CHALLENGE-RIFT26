import networkx as nx
from typing import List, Set, Dict
from uuid import uuid4
from datetime import timedelta
from app.utils.ring_utils import generate_ring_id
from app.patterns.base_detector import BaseDetector
from app.models.detection import DetectionResult
from app.config import CYCLE_MIN_LENGTH, CYCLE_MAX_LENGTH


class CycleDetector(BaseDetector):

    def detect(self, graph: nx.MultiDiGraph) -> List[DetectionResult]:

        # Convert to DiGraph for simple cycle detection (structure only)
        simple_graph = nx.DiGraph()
        simple_graph.add_nodes_from(graph.nodes())
        simple_graph.add_edges_from(graph.edges())

        if graph.number_of_edges() > 20000:
             return []

        raw_cycles = list(nx.simple_cycles(simple_graph))

        # Filter by length constraints
        filtered_cycles = [
            cycle for cycle in raw_cycles
            if CYCLE_MIN_LENGTH <= len(cycle) <= CYCLE_MAX_LENGTH
        ]

        if not filtered_cycles:
            return []

        # Canonicalize cycles to avoid duplicates
        canonical_cycles = self._canonicalize_cycles(filtered_cycles)

        # Merge overlapping cycles into rings
        merged_rings = self._merge_overlapping_cycles(canonical_cycles)

        # Build DetectionResults
        results = []
        for ring_nodes in merged_rings:

            ring_id = generate_ring_id(sorted(list(ring_nodes)), "cycle")
            risk_score, evidence = self._compute_ring_risk(graph, ring_nodes)

            results.append(
                DetectionResult(
                    ring_id=ring_id,
                    pattern_type="cycle",
                    member_accounts=sorted(list(ring_nodes)),
                    risk_score=round(risk_score, 2),
                    evidence=evidence
                )
            )

        return results

    # -------------------------
    # Internal Helpers
    # -------------------------

    def _canonicalize_cycles(self, cycles: List[List[str]]) -> List[Set[str]]:
        """
        Convert cycles to frozensets to remove duplicates regardless of rotation.
        """
        unique_cycles = set()
        for cycle in cycles:
            unique_cycles.add(frozenset(cycle))
        return [set(c) for c in unique_cycles]

    def _merge_overlapping_cycles(self, cycles: List[Set[str]]) -> List[Set[str]]:
        """
        Merge cycles that share at least one node into a single ring.
        """
        merged = []

        for cycle in cycles:
            merged_into_existing = False

            for ring in merged:
                if not cycle.isdisjoint(ring):
                    ring.update(cycle)
                    merged_into_existing = True
                    break

            if not merged_into_existing:
                merged.append(set(cycle))

        # One more pass to ensure full merging
        final_merged = []
        while merged:
            first = merged.pop(0)
            changed = True
            while changed:
                changed = False
                for other in merged[:]:
                    if not first.isdisjoint(other):
                        first.update(other)
                        merged.remove(other)
                        changed = True
            final_merged.append(first)

        return final_merged

    def _compute_ring_risk(self, graph: nx.MultiDiGraph, ring_nodes: Set[str]):
        """
        Risk scoring based on:
        - Total transaction value within ring
        - Time compression (shorter duration = riskier)
        - Ring size (shorter cycles = more suspicious)
        """

        total_value = 0
        timestamps = []

        for u in ring_nodes:
            for v in ring_nodes:
                if graph.has_edge(u, v):
                    edges = graph.get_edge_data(u, v)
                    for _, edge_data in edges.items():
                        total_value += edge_data["amount"]
                        timestamps.append(edge_data["timestamp"])

        if timestamps:
            duration_hours = (
                (max(timestamps) - min(timestamps)).total_seconds() / 3600
            )
        else:
            duration_hours = 0

        # Normalize components
        value_score = min(total_value / 10000, 1.0)  # scale cap
        velocity_score = 1.0 if duration_hours <= 24 else max(0, 1 - duration_hours / 168)
        size_score = 1 / len(ring_nodes)

        # Weighted risk model
        risk = (
            0.4 * value_score +
            0.4 * velocity_score +
            0.2 * size_score
        ) * 100

        evidence = {
            "total_value": round(total_value, 2),
            "duration_hours": round(duration_hours, 2),
            "ring_size": len(ring_nodes)
        }

        return min(risk, 100), evidence
