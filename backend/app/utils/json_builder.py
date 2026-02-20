# app/utils/json_builder.py

import time
from typing import List
from app.models.detection import DetectionResult


class JSONBuilder:

    def build(
        self,
        suspicious_accounts: List[dict],
        rings: List[DetectionResult],
        total_accounts: int,
        start_time: float
    ):

        processing_time = round(time.time() - start_time, 2)

        # ------------------------------
        # Format Fraud Rings
        # ------------------------------
        fraud_rings = []

        for ring in rings:
            fraud_rings.append({
                "ring_id": ring.ring_id,
                "member_accounts": sorted(ring.member_accounts),
                "pattern_type": ring.pattern_type,
                "risk_score": round(ring.risk_score, 2)
            })

        # ------------------------------
        # Format Suspicious Accounts
        # ------------------------------
        formatted_accounts = []

        for acc in suspicious_accounts:

            # Spec requires single ring_id.
            # Choose highest-risk ring if multiple.
            ring_id = acc["ring_ids"][0] if acc["ring_ids"] else None

            formatted_accounts.append({
                "account_id": acc["account_id"],
                "suspicion_score": round(acc["suspicion_score"], 2),
                "detected_patterns": sorted(acc["detected_patterns"]),
                "ring_id": ring_id
            })

        # Ensure sorted descending
        formatted_accounts.sort(
            key=lambda x: x["suspicion_score"],
            reverse=True
        )

        # ------------------------------
        # Summary
        # ------------------------------
        summary = {
            "total_accounts_analyzed": total_accounts,
            "suspicious_accounts_flagged": len(formatted_accounts),
            "fraud_rings_detected": len(fraud_rings),
            "processing_time_seconds": processing_time
        }

        return {
            "suspicious_accounts": formatted_accounts,
            "fraud_rings": fraud_rings,
            "summary": summary
        }
