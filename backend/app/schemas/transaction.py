from pydantic import BaseModel
from datetime import datetime


class TransactionCreate(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    merchant: str
    location: str
    device_id: str
    timestamp: datetime | None = None

    previous_transactions: int = 0
    is_new_device: int = 0
    distance_from_previous: float = 0.0
    is_night: int = 0


class TransactionResponse(TransactionCreate):
    id: int
    is_fraud: bool

    # Fraud detection results
    ml_score: float
    anomaly_score: float
    rule_score: float
    risk_score: float
    risk_level: str
    reasons: list[str]

    class Config:
        from_attributes = True