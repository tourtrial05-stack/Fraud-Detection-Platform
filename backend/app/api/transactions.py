from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import joblib
import numpy as np
import pandas as pd

from backend.app.database import get_db
from backend.app.models.transaction import Transaction
from backend.app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
)
from backend.app.services.risk_engine import calculate_rule_score


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


# Load trained models once when the backend starts
fraud_model = joblib.load("ml/models/fraud_model_v2.pkl")
anomaly_model = joblib.load("ml/models/anomaly_model.pkl")
anomaly_scaler = joblib.load("ml/models/anomaly_scaler.pkl")


def get_transaction_hour(transaction):
    """Safely extract the transaction hour."""

    if transaction.timestamp:
        return transaction.timestamp.hour

    return 0


def calculate_ml_score(transaction):
    """Calculate supervised machine-learning fraud probability."""

    features = pd.DataFrame(
        [[
            transaction.amount,
            get_transaction_hour(transaction),
            transaction.previous_transactions,
            transaction.is_new_device,
            transaction.distance_from_previous,
            transaction.is_night,
            int(transaction.amount > 10000),
            int(transaction.distance_from_previous > 500),
            int(transaction.previous_transactions < 2),
        ]],
        columns=[
            "amount",
            "hour",
            "previous_transactions",
            "is_new_device",
            "distance_from_previous",
            "is_night",
            "is_high_amount",
            "is_large_distance",
            "is_low_history",
        ],
    )

    probability = fraud_model.predict_proba(features)[0][1]

    return round(float(probability * 100), 2)


def calculate_anomaly_score(transaction):
    """Calculate anomaly score using Isolation Forest."""

    features = pd.DataFrame(
        [[
            transaction.amount,
            get_transaction_hour(transaction),
            transaction.previous_transactions,
            transaction.is_new_device,
            transaction.distance_from_previous,
        ]],
        columns=[
            "amount",
            "hour",
            "previous_transactions",
            "is_new_device",
            "distance_from_previous",
        ],
    )

    scaled_features = anomaly_scaler.transform(features)

    decision_score = anomaly_model.decision_function(scaled_features)[0]

    anomaly_score = np.clip(
        (0.5 - decision_score) * 100,
        0,
        100,
    )

    return round(float(anomaly_score), 2)


def build_reasons(transaction, ml_score, anomaly_score):
    """Build clear, human-readable fraud explanations."""

    _, reasons = calculate_rule_score(transaction)

    if ml_score >= 70:
        reasons.append(
            "Machine learning model detected a high fraud probability"
        )

    if anomaly_score >= 70:
        reasons.append(
            "Transaction behavior is highly unusual compared with normal activity"
        )

    return reasons


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    """
    Create and score a new transaction.
    """

    # Prevent duplicate transaction IDs
    existing_transaction = (
        db.query(Transaction)
        .filter(
            Transaction.transaction_id == transaction.transaction_id
        )
        .first()
    )

    if existing_transaction:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Transaction ID '{transaction.transaction_id}' "
                "already exists. Please use a unique transaction ID."
            ),
        )

    # Calculate all risk signals
    ml_score = calculate_ml_score(transaction)

    anomaly_score = calculate_anomaly_score(transaction)

    rule_score, _ = calculate_rule_score(transaction)

    # Combine the three signals
    risk_score = round(
        min(
            (ml_score * 0.50)
            + (anomaly_score * 0.25)
            + (rule_score * 0.25),
            100,
        ),
        2,
    )

    # Assign risk category
    if risk_score >= 70:
        risk_level = "HIGH"
        is_fraud = True

    elif risk_score >= 40:
        risk_level = "MEDIUM"
        is_fraud = False

    else:
        risk_level = "LOW"
        is_fraud = False

    reasons = build_reasons(
        transaction,
        ml_score,
        anomaly_score,
    )

    new_transaction = Transaction(
        transaction_id=transaction.transaction_id,
        user_id=transaction.user_id,
        amount=transaction.amount,
        merchant=transaction.merchant,
        location=transaction.location,
        device_id=transaction.device_id,
        timestamp=transaction.timestamp,
        previous_transactions=transaction.previous_transactions,
        is_new_device=transaction.is_new_device,
        distance_from_previous=transaction.distance_from_previous,
        is_night=transaction.is_night,
        ml_score=ml_score,
        anomaly_score=anomaly_score,
        rule_score=rule_score,
        risk_score=risk_score,
        risk_level=risk_level,
        is_fraud=is_fraud,
    )

    try:
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                f"Transaction ID '{transaction.transaction_id}' "
                "already exists. Please use a unique transaction ID."
            ),
        )

    return {
        **transaction.model_dump(),
        "id": new_transaction.id,
        "is_fraud": is_fraud,
        "ml_score": ml_score,
        "anomaly_score": anomaly_score,
        "rule_score": rule_score,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
    }


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
):
    """
    Return all transactions with fraud explanations.
    """

    transactions = (
        db.query(Transaction)
        .order_by(Transaction.id.desc())
        .all()
    )

    results = []

    for transaction in transactions:
        reasons = build_reasons(
            transaction,
            transaction.ml_score or 0,
            transaction.anomaly_score or 0,
        )

        results.append(
            {
                "id": transaction.id,
                "transaction_id": transaction.transaction_id,
                "user_id": transaction.user_id,
                "amount": transaction.amount,
                "merchant": transaction.merchant,
                "location": transaction.location,
                "device_id": transaction.device_id,
                "timestamp": transaction.timestamp,
                "is_fraud": transaction.is_fraud,
                "previous_transactions": transaction.previous_transactions,
                "is_new_device": transaction.is_new_device,
                "distance_from_previous": transaction.distance_from_previous,
                "is_night": transaction.is_night,
                "ml_score": transaction.ml_score or 0,
                "anomaly_score": transaction.anomaly_score or 0,
                "rule_score": transaction.rule_score or 0,
                "risk_score": transaction.risk_score or 0,
                "risk_level": transaction.risk_level or "LOW",
                "reasons": reasons,
            }
        )

    return results