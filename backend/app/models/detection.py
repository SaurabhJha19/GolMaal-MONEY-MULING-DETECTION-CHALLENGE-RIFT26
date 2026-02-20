from pydantic import BaseModel
from typing import List, Dict


class DetectionResult(BaseModel):
    ring_id: str
    pattern_type: str
    member_accounts: List[str]
    risk_score: float
    evidence: Dict
