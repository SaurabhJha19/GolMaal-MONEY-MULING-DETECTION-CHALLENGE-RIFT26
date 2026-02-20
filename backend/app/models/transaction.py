from pydantic import BaseModel, field_validator
from datetime import datetime


class Transaction(BaseModel):
    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float
    timestamp: datetime

    @field_validator("transaction_id", "sender_id", "receiver_id")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        v = str(v).strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v.upper()

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
