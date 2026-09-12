from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str
    full_name: str


class DecisionRequest(BaseModel):
    decision: Literal["APPROVE", "REJECT"]
    reason: str | None = None


class AuditLogResponse(BaseModel):
    id: int
    transaction_id: str
    analyst_username: str
    analyst_role: str
    action: str
    decision: str
    reason: str | None
    created_at: datetime