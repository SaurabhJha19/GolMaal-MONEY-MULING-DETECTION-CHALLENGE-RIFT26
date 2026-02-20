import networkx as nx
from typing import List, Dict, Set
from uuid import uuid4
from datetime import timedelta
from app.utils.ring_utils import generate_ring_id
from app.patterns.base_detector import BaseDetector
from app.models.detection import DetectionResult
from app.config import SMURFING_THRESHOLD, SMURFING_WINDOW_HOURS


class SmurfingDetector(BaseDetector):

    def detect(self, graph: nx.MultiDiGraph) -> List[DetectionResult]:

        results = []

        for node in graph.nodes():

            fan_in_result = self._detect_fan_in(graph, node)
            if fan_in_result:
                results.append(fan_in_result)

            fan_out_result = self._detect_fan_out(graph, node)
            if fan_out_result:
                results.append(fan_out_result)

        return results

    # -----------------------------------
    # Fan-In Detection
    # -----------------------------------

    def _detect_fan_in(self, graph: nx.MultiDiGraph, node: str):

        in_edges = list(graph.in_edges(node, data=True))
        if len(in_edges) < SMURFING_THRESHOLD:
            return None

        # Sort by timestamp
        in_edges.sort(key=lambda x: x[2]["timestamp"])

        window_start = 0

        for window_end in range(len(in_edges)):

            while (
                in_edges[window_end][2]["timestamp"] -
                in_edges[window_start][2]["timestamp"]
            ).total_seconds() > SMURFING_WINDOW_HOURS * 3600:
                window_start += 1

            window_slice = in_edges[window_start:window_end + 1]

            unique_senders = set(edge[0] for edge in window_slice)

            if len(unique_senders) >= SMURFING_THRESHOLD:

                ring_nodes = set(unique_senders)
                ring_nodes.add(node)

                risk_score, evidence = self._compute_risk(window_slice, "fan_in")

                return DetectionResult(
                    ring_id=generate_ring_id(sorted(list(ring_nodes)), "cycle"),
                    pattern_type="smurfing_fan_in",
                    member_accounts=sorted(list(ring_nodes)),
                    risk_score=round(risk_score, 2),
                    evidence=evidence
                )

        return None

    # -----------------------------------
    # Fan-Out Detection
    # -----------------------------------

    def _detect_fan_out(self, graph: nx.MultiDiGraph, node: str):

        out_edges = list(graph.out_edges(node, data=True))
        if len(out_edges) < SMURFING_THRESHOLD:
            return None

        # Sort by timestamp
        out_edges.sort(key=lambda x: x[2]["timestamp"])

        window_start = 0

        for window_end in range(len(out_edges)):

            while (
                out_edges[window_end][2]["timestamp"] -
                out_edges[window_start][2]["timestamp"]
            ).total_seconds() > SMURFING_WINDOW_HOURS * 3600:
                window_start += 1

            window_slice = out_edges[window_start:window_end + 1]

            unique_receivers = set(edge[1] for edge in window_slice)

            if len(unique_receivers) >= SMURFING_THRESHOLD:

                ring_nodes = set(unique_receivers)
                ring_nodes.add(node)

                risk_score, evidence = self._compute_risk(window_slice, "fan_out")

                return DetectionResult(
                    ring_id=f"RING_{uuid4().hex[:8].upper()}",
                    pattern_type="smurfing_fan_out",
                    member_accounts=sorted(list(ring_nodes)),
                    risk_score=round(risk_score, 2),
                    evidence=evidence
                )

        return None

    # -----------------------------------
    # Risk Computation
    # -----------------------------------

    def _compute_risk(self, edges, pattern_type: str):

        total_value = sum(edge[2]["amount"] for edge in edges)
        timestamps = [edge[2]["timestamp"] for edge in edges]

        duration_hours = (
            (max(timestamps) - min(timestamps)).total_seconds() / 3600
            if timestamps else 0
        )

        value_score = min(total_value / 20000, 1.0)
        velocity_score = 1.0 if duration_hours <= 24 else max(0, 1 - duration_hours / 168)
        density_score = min(len(edges) / (SMURFING_THRESHOLD * 2), 1.0)

        risk = (
            0.4 * value_score +
            0.4 * velocity_score +
            0.2 * density_score
        ) * 100

        evidence = {
            "pattern": pattern_type,
            "transaction_count_in_window": len(edges),
            "total_value": round(total_value, 2),
            "duration_hours": round(duration_hours, 2)
        }

        return min(risk, 100), evidence
