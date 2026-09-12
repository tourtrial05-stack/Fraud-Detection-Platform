from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.transaction import Transaction
from backend.app.models.operations import Feedback
from backend.app.core.security import get_current_user


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    transactions = db.query(Transaction).all()
    feedback = db.query(Feedback).all()

    total = len(transactions)

    high = sum(
        1 for t in transactions
        if t.risk_level == "HIGH"
    )

    medium = sum(
        1 for t in transactions
        if t.risk_level == "MEDIUM"
    )

    low = sum(
        1 for t in transactions
        if t.risk_level == "LOW"
    )

    confirmed_fraud = sum(
        1 for f in feedback
        if f.analyst_label == "FRAUD"
    )

    confirmed_legit = sum(
        1 for f in feedback
        if f.analyst_label == "LEGIT"
    )

    return {
        "total_transactions": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "model_flagged_fraud": sum(
            1 for t in transactions
            if t.is_fraud
        ),
        "reviewed_transactions": len(feedback),
        "confirmed_fraud": confirmed_fraud,
        "confirmed_legit": confirmed_legit
    }


@router.get("/model-performance")
def model_performance(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    feedback = db.query(Feedback).all()

    if not feedback:
        return {
            "feedback_count": 0,
            "accuracy": 0,
            "precision": 0,
            "recall": 0,
            "f1_score": 0,
            "message": "No analyst feedback available yet"
        }

    tp = tn = fp = fn = 0

    for item in feedback:

        prediction = bool(item.model_prediction)
        actual = item.analyst_label == "FRAUD"

        if prediction and actual:
            tp += 1
        elif not prediction and not actual:
            tn += 1
        elif prediction and not actual:
            fp += 1
        elif not prediction and actual:
            fn += 1

    total = tp + tn + fp + fn

    accuracy = (
        (tp + tn) / total
        if total else 0
    )

    precision = (
        tp / (tp + fp)
        if tp + fp else 0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    return {
        "feedback_count": total,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1 * 100, 2)
    }