import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# -----------------------------
# 1. Load dataset
# -----------------------------

DATA_PATH = "ml/data/fraud_transactions.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print(f"Total records: {len(df)}")


# -----------------------------
# 2. Select behavioural features
# -----------------------------

features = [
    "amount",
    "hour",
    "previous_transactions",
    "is_new_device",
    "distance_from_previous"
]

X = df[features]


# -----------------------------
# 3. Scale features
# -----------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# -----------------------------
# 4. Create Isolation Forest
# -----------------------------

model = IsolationForest(
    n_estimators=200,
    contamination=0.08,
    random_state=42,
    n_jobs=-1
)


# -----------------------------
# 5. Train model
# -----------------------------

print("\nTraining Isolation Forest...")

model.fit(X_scaled)

print("Anomaly model training completed!")


# -----------------------------
# 6. Generate anomaly predictions
# -----------------------------

predictions = model.predict(X_scaled)

anomaly_count = (predictions == -1).sum()

print(f"\nAnomalies detected: {anomaly_count}")


# -----------------------------
# 7. Save model + scaler
# -----------------------------

MODEL_PATH = "ml/models/anomaly_model.pkl"
SCALER_PATH = "ml/models/anomaly_scaler.pkl"

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    scaler,
    SCALER_PATH
)

print(f"Anomaly model saved to: {MODEL_PATH}")
print(f"Scaler saved to: {SCALER_PATH}")