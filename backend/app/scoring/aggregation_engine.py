from typing import List, Dict
from collections import defaultdict
from app.models.detection import DetectionResult
from app.config import WEIGHTS, MIN_SUSPICION_SCORE
import math

class AggregationEngine:

    def aggregate(
        self,
        graph,
        cycle_results: List[DetectionResult],
        smurfing_results: List[DetectionResult],
        shell_results: List[DetectionResult],
    ):

        all_rings = cycle_results + smurfing_results + shell_results

        account_risk_map = defaultdict(lambda: {
            "patterns": [],
            "ring_ids": set(),
            "raw_score": 0.0
        })

        # ----------------------------
        # Aggregate Ring Contributions
        # ----------------------------
        for ring in all_rings:

            for account in ring.member_accounts:

                account_risk_map[account]["patterns"].append(ring.pattern_type)
                account_risk_map[account]["ring_ids"].add(ring.ring_id)

                # Contribution model
                if ring.pattern_type == "cycle":
                    weight = WEIGHTS["cycle"]
                elif "smurfing" in ring.pattern_type:
                    weight = WEIGHTS["smurfing"]
                elif ring.pattern_type == "shell_chain":
                    weight = WEIGHTS["shell_chain"]
                else:
                    weight = 0

                account_risk_map[account]["raw_score"] += (
                    weight * (ring.risk_score / 100)
                )

        # ----------------------------
        # Add Velocity Feature
        # ----------------------------
        for account in account_risk_map:

            features = graph.nodes[account]["features"]

            velocity = self._compute_velocity_score(features)
            anomaly = self._compute_anomaly_score(features)

            account_risk_map[account]["raw_score"] += WEIGHTS["velocity"] * velocity
            account_risk_map[account]["raw_score"] += WEIGHTS["anomaly"] * anomaly

        # ----------------------------
        # False Positive Mitigation
        # ----------------------------
        for account in account_risk_map:

            if self._is_merchant_like(graph, account):
                account_risk_map[account]["raw_score"] *= 0.6

        # ----------------------------
        # Normalize to 0–100
        # ----------------------------
        suspicious_accounts = []

        for account, data in account_risk_map.items():
            raw = data["raw_score"]
            k = 3.5 
            amplified = 1 - math.exp(-k * raw)

            score = min(amplified * 100, 100)
            if score < MIN_SUSPICION_SCORE:
                continue

            suspicious_accounts.append({
                "account_id": account,
                "suspicion_score": round(score, 2),
                "detected_patterns": list(set(data["patterns"])),
                "ring_ids": list(data["ring_ids"])
            })

        suspicious_accounts.sort(
            key=lambda x: x["suspicion_score"],
            reverse=True
        )

        unique_rings = {}
        for ring in all_rings:
            unique_rings[ring.ring_id] = ring

        all_rings = list(unique_rings.values())


        return suspicious_accounts, all_rings

    # ----------------------------------------
    # Feature-Level Helpers
    # ----------------------------------------

    def _compute_velocity_score(self, features):

        duration = features["activity_duration_hours"]
        tx_count = features["transaction_count"]

        if duration == 0:
            return 0

        tx_per_hour = tx_count / duration

        return min(tx_per_hour / 5, 1.0)

    def _compute_anomaly_score(self, features):

        in_out_diff = abs(features["total_in"] - features["total_out"])
        total_volume = features["total_in"] + features["total_out"]

        if total_volume == 0:
            return 0

        imbalance_ratio = in_out_diff / total_volume

        return min(imbalance_ratio, 1.0)

    def _is_merchant_like(self, graph, account):

        features = graph.nodes[account]["features"]

        # High volume, long activity, no circular behavior
        if (
            features["transaction_count"] > 20 and
            features["activity_duration_hours"] > 720 and  # 30 days
            features["in_degree"] > 10 and
            features["out_degree"] > 10
        ):
            return True

        return False
