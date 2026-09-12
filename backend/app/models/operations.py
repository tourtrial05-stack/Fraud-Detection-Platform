from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from backend.app.database import Base


class Analyst(Base):
    __tablename__ = "analysts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    role = Column(String, default="ANALYST")
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, nullable=False, index=True)
    analyst_username = Column(String, nullable=False)
    analyst_role = Column(String, nullable=False)
    action = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, nullable=False, index=True)
    analyst_username = Column(String, nullable=False)
    analyst_label = Column(String, nullable=False)
    model_prediction = Column(Boolean, nullable=False)
    model_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)