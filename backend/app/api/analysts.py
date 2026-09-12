from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.transaction import Transaction
from backend.app.models.operations import AuditLog, Feedback
from backend.app.schemas.operations import DecisionRequest
from backend.app.core.security import get_current_user


router = APIRouter(
    prefix="/analysts",
    tags=["Fraud Operations"]
)


@router.post("/transactions/{transaction_id}/decision")
def review_transaction(
    transaction_id: str,
    request: DecisionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role not in ["ADMIN", "ANALYST"]:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to review transactions"
        )

    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_id == transaction_id
        )
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    # APPROVE = legitimate
    # REJECT = confirmed fraud
    analyst_label = (
        "LEGIT"
        if request.decision == "APPROVE"
        else "FRAUD"
    )

    audit = AuditLog(
        transaction_id=transaction.transaction_id,
        analyst_username=current_user.username,
        analyst_role=current_user.role,
        action="TRANSACTION_REVIEW",
        decision=request.decision,
        reason=request.reason
    )

    feedback = Feedback(
        transaction_id=transaction.transaction_id,
        analyst_username=current_user.username,
        analyst_label=analyst_label,
        model_prediction=bool(transaction.is_fraud),
        model_score=float(transaction.risk_score or 0)
    )

    db.add(audit)
    db.add(feedback)
    db.commit()

    return {
        "message": "Transaction review recorded",
        "transaction_id": transaction.transaction_id,
        "decision": request.decision,
        "analyst": current_user.username,
        "analyst_label": analyst_label
    }


@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return logs


@router.get("/reviews")
def get_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    latest_reviews = {}

    for log in logs:

        if log.transaction_id not in latest_reviews:

            latest_reviews[log.transaction_id] = {
                "transaction_id": log.transaction_id,
                "decision": log.decision,
                "analyst": log.analyst_username,
                "reason": log.reason,
                "created_at": log.created_at
            }

    return list(latest_reviews.values())