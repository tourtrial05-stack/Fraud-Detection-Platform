from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.transaction import Transaction
from backend.app.core.security import get_current_user


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"]
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = PROJECT_ROOT / "ml" / "data" / "fraud_transactions.csv"


@router.get("/drift")
def detect_drift(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    baseline = pd.read_csv(DATA_PATH)

    transactions = (
        db.query(Transaction)
        .order_by(Transaction.timestamp.desc())
        .limit(100)
        .all()
    )

    if len(transactions) < 10:

        return {
            "status": "INSUFFICIENT_DATA",
            "retraining_required": False,
            "message": "Need at least 10 recent transactions"
        }

    baseline_features = {
        "amount": baseline["amount"].mean(),
        "distance": baseline["distance_from_previous"].mean(),
        "new_device_rate": baseline["is_new_device"].mean(),
        "night_rate": baseline["is_night"].mean()
    }

    recent_amount = sum(
        t.amount for t in transactions
    ) / len(transactions)

    recent_distance = sum(
        t.distance_from_previous for t in transactions
    ) / len(transactions)

    recent_new_device = sum(
        t.is_new_device for t in transactions
    ) / len(transactions)

    recent_night = sum(
        t.is_night for t in transactions
    ) / len(transactions)

    amount_shift = abs(
        recent_amount - baseline_features["amount"]
    ) / max(baseline_features["amount"], 1)

    distance_shift = abs(
        recent_distance - baseline_features["distance"]
    ) / max(baseline_features["distance"], 1)

    new_device_shift = abs(
        recent_new_device -
        baseline_features["new_device_rate"]
    )

    night_shift = abs(
        recent_night -
        baseline_features["night_rate"]
    )

    drift_score = max(
        amount_shift,
        distance_shift,
        new_device_shift,
        night_shift
    )

    if drift_score >= 0.50:
        status = "HIGH"
    elif drift_score >= 0.25:
        status = "MEDIUM"
    else:
        status = "LOW"

    return {
        "status": status,
        "drift_score": round(drift_score, 3),
        "retraining_required": drift_score >= 0.50,
        "recent_transactions": len(transactions),
        "feature_shifts": {
            "amount": round(amount_shift, 3),
            "distance": round(distance_shift, 3),
            "new_device_rate": round(new_device_shift, 3),
            "night_rate": round(night_shift, 3)
        }
    }