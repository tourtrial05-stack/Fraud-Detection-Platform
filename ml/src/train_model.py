import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)


# -----------------------------
# 1. Load dataset
# -----------------------------

DATA_PATH = "ml/data/fraud_transactions.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print(f"Total records: {len(df)}")


# -----------------------------
# 2. Select features
# -----------------------------

features = [
    "amount",
    "hour",
    "previous_transactions",
    "is_new_device",
    "distance_from_previous",
    "is_night",
    "is_high_amount",
    "is_large_distance",
    "is_low_history"
]

X = df[features]
y = df["is_fraud"]


# -----------------------------
# 3. Split data
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")


# -----------------------------
# 4. Create Random Forest
# -----------------------------

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    min_samples_leaf=2,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# -----------------------------
# 5. Train model
# -----------------------------

print("\nTraining Model V2...")

model.fit(X_train, y_train)

print("Model V2 training completed!")


# -----------------------------
# 6. Predictions
# -----------------------------

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# -----------------------------
# 7. Evaluation
# -----------------------------

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

auc = roc_auc_score(
    y_test,
    y_probability
)

print(f"\nROC-AUC Score: {auc:.4f}")


# -----------------------------
# 8. Feature importance
# -----------------------------

print("\nFeature Importance:")

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    by="importance",
    ascending=False
)

print(importance.to_string(index=False))


# -----------------------------
# 9. Save Model V2
# -----------------------------

MODEL_PATH = "ml/models/fraud_model_v2.pkl"

joblib.dump(
    model,
    MODEL_PATH
)

print(f"\nModel V2 saved to: {MODEL_PATH}")