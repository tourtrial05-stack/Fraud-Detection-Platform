import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

N = 10000

# -----------------------------
# Basic transaction information
# -----------------------------

transaction_ids = [f"TXN{i:06d}" for i in range(1, N + 1)]

user_ids = [
    f"USER{np.random.randint(1, 2001):05d}"
    for _ in range(N)
]

merchants = [
    "Amazon",
    "Flipkart",
    "Walmart",
    "Apple",
    "Netflix",
    "Uber",
    "Swiggy",
    "Zomato",
    "Myntra",
    "Paytm"
]

locations = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Chennai",
    "Hyderabad",
    "Kolkata",
    "Pune",
    "Ahmedabad"
]

merchant_data = np.random.choice(merchants, N)
location_data = np.random.choice(locations, N)

# -----------------------------
# Device information
# -----------------------------

device_data = np.random.choice(
    [
        "DEVICE_A",
        "DEVICE_B",
        "DEVICE_C",
        "DEVICE_D",
        "DEVICE_E"
    ],
    N
)

is_new_device = np.random.choice(
    [0, 1],
    N,
    p=[0.85, 0.15]
)

# -----------------------------
# Transaction amount
# -----------------------------

amounts = np.random.lognormal(
    mean=7.0,
    sigma=0.9,
    size=N
)

amounts = np.round(amounts, 2)

# -----------------------------
# Transaction time
# -----------------------------

start_date = datetime(2026, 1, 1)

timestamps = [
    start_date + timedelta(
        minutes=int(
            np.random.randint(
                0,
                365 * 24 * 60
            )
        )
    )
    for _ in range(N)
]

hours = np.array([
    timestamp.hour
    for timestamp in timestamps
])

# -----------------------------
# User behaviour
# -----------------------------

previous_transactions = np.random.randint(
    0,
    50,
    N
)

distance_from_previous = np.random.exponential(
    scale=20,
    size=N
)

distance_from_previous = np.round(
    distance_from_previous,
    2
)

# -----------------------------
# Behavioural features
# -----------------------------

is_night = (
    (hours >= 0) & (hours <= 5)
).astype(int)

is_high_amount = (
    amounts > 10000
).astype(int)

is_large_distance = (
    distance_from_previous > 500
).astype(int)

is_low_history = (
    previous_transactions < 2
).astype(int)

# -----------------------------
# Fraud probability
# -----------------------------

fraud_probability = np.full(
    N,
    0.005
)

# High amount
fraud_probability += (
    is_high_amount * 0.35
)

# New device
fraud_probability += (
    is_new_device * 0.25
)

# Impossible/large travel
fraud_probability += (
    is_large_distance * 0.30
)

# Night transaction
fraud_probability += (
    is_night * 0.15
)

# Very little transaction history
fraud_probability += (
    is_low_history * 0.15
)

# Combined suspicious behaviour
suspicious_count = (
    is_high_amount
    + is_new_device
    + is_large_distance
    + is_night
)

fraud_probability += np.where(
    suspicious_count >= 3,
    0.25,
    0
)

fraud_probability = np.clip(
    fraud_probability,
    0,
    0.95
)

# -----------------------------
# Generate fraud labels
# -----------------------------

is_fraud = np.random.binomial(
    1,
    fraud_probability
)

# -----------------------------
# Create DataFrame
# -----------------------------

df = pd.DataFrame({
    "transaction_id": transaction_ids,
    "user_id": user_ids,
    "amount": amounts,
    "merchant": merchant_data,
    "location": location_data,
    "device_id": device_data,
    "timestamp": timestamps,
    "hour": hours,
    "previous_transactions": previous_transactions,
    "is_new_device": is_new_device,
    "distance_from_previous": distance_from_previous,
    "is_night": is_night,
    "is_high_amount": is_high_amount,
    "is_large_distance": is_large_distance,
    "is_low_history": is_low_history,
    "is_fraud": is_fraud
})

# -----------------------------
# Save dataset
# -----------------------------

output_file = "ml/data/fraud_transactions.csv"

df.to_csv(
    output_file,
    index=False
)

print("Dataset generated successfully!")
print(f"Total transactions: {len(df)}")
print(f"Fraud transactions: {df['is_fraud'].sum()}")
print(
    f"Fraud percentage: "
    f"{df['is_fraud'].mean() * 100:.2f}%"
)
print(f"Saved to: {output_file}")