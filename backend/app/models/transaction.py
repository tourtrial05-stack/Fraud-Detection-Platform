from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime

from backend.app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)

    amount = Column(Float)
    merchant = Column(String)

    location = Column(String)
    device_id = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)

    previous_transactions = Column(Integer, default=0)
    is_new_device = Column(Integer, default=0)
    distance_from_previous = Column(Float, default=0.0)
    is_night = Column(Integer, default=0)

    # Fraud detection results
    ml_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    rule_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)

    risk_level = Column(String, default="LOW")

    # Final fraud decision
    is_fraud = Column(Boolean, default=False)