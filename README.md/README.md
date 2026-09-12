
# AI Fraud Detection & Fraud Operations Platform

An end-to-end fraud detection and analyst operations platform that combines supervised machine learning, anomaly detection, deterministic business rules, and human review to identify suspicious financial transactions.

## Overview

The platform analyzes transactions using three independent signals:

1. **Supervised machine learning** detects known fraud patterns.
2. **Anomaly detection** identifies unusual transaction behavior.
3. **Rule-based detection** applies deterministic business rules such as unusually high amounts, new devices, unusual hours, and large location changes.

These signals are combined into a final fraud-risk score. Analysts can investigate suspicious transactions, approve or reject them, and track decisions through audit logs.

## Key Features

- Supervised fraud classification using Random Forest
- Anomaly detection using Isolation Forest
- Rule-based fraud detection engine
- Combined risk scoring system
- Low, medium, and high risk classification
- Human-readable fraud explanations
- Real-time transaction dashboard
- Analyst authentication
- Analyst approve/reject workflow
- Audit logging of analyst decisions
- Fraud analytics and performance monitoring
- Basic transaction drift monitoring
- REST API using FastAPI
- Interactive frontend using React
- SQLite database for local development

## System Architecture

```text
Transaction Input
       |
       v
FastAPI Backend
       |
       +----------------------+
       |                      |
       v                      v
Supervised ML Model     Anomaly Model
(Random Forest)         (Isolation Forest)
       |                      |
       +----------+-----------+
                  |
                  v
          Rule-Based Engine
                  |
                  v
          Combined Risk Score
                  |
                  v
       Risk Level and Explanations
                  |
                  v
          React Dashboard
                  |
                  v
       Analyst Investigation
                  |
                  v
       Approve / Reject Decision
                  |
                  v
            Audit Logs
```

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT authentication
- Uvicorn

### Machine Learning

- Pandas
- NumPy
- Scikit-learn
- Random Forest Classifier
- Isolation Forest
- StandardScaler
- Joblib

### Frontend

- React
- Vite
- Axios
- Recharts
- React Leaflet
- CSS

### Development Tools

- Git
- GitHub
- VS Code
- PowerShell

## Machine Learning Models

### Supervised Fraud Model

The supervised model uses transaction features such as:

- Transaction amount
- Transaction hour
- Previous transaction count
- New-device indicator
- Distance from previous transaction
- Night-time indicator
- High-amount indicator
- Large-distance indicator
- Low-history indicator

The model produces a fraud probability that is converted into a percentage score.

### Anomaly Detection Model

The Isolation Forest model identifies transactions that differ significantly from normal transaction behavior.

It uses features including:

- Amount
- Hour
- Previous transactions
- New-device indicator
- Distance from previous transaction

### Rule Engine

The rule engine adds deterministic risk points for suspicious conditions:

- High transaction amount
- New device
- Large distance from previous activity
- Unusual transaction hour
- Very low transaction history

## Risk Scoring

The final risk score combines the three detection signals:

```text
Final Risk Score =
    50% Supervised ML Score
  + 25% Anomaly Score
  + 25% Rule Score
```

Risk levels:

| Risk Score | Risk Level |
|------------|------------|
| 0–39       | LOW        |
| 40–69      | MEDIUM     |
| 70–100     | HIGH       |

High-risk transactions are marked for analyst investigation.

## Model Performance

The current supervised model achieved approximately:

| Metric | Result |
|--------|--------|
| Accuracy | 79% |
| Precision | 25% |
| Recall | 67% |
| F1 Score | 36% |
| ROC-AUC | 0.842 |

These results are based on the generated development dataset and are intended for portfolio demonstration and experimentation.

## Project Structure

```text
AI-Fraud-Detection-Platform/
│
├── backend/
│   └── app/
│       ├── api/
│       │   ├── analysts.py
│       │   ├── analytics.py
│       │   ├── auth.py
│       │   ├── monitoring.py
│       │   └── transactions.py
│       ├── core/
│       │   └── security.py
│       ├── models/
│       │   ├── operations.py
│       │   └── transaction.py
│       ├── schemas/
│       │   ├── operations.py
│       │   └── transaction.py
│       ├── services/
│       │   └── risk_engine.py
│       ├── database.py
│       └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── ml/
│   ├── data/
│   │   ├── fraud_transactions.csv
│   │   └── generate_data.py
│   ├── models/
│   │   ├── fraud_model_v2.pkl
│   │   ├── anomaly_model.pkl
│   │   └── anomaly_scaler.pkl
│   └── src/
│       ├── train_model.py
│       └── anomaly_model.py
│
├── tests/
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tourtrial05-stack/Fraud-Detection-Platform.git
cd Fraud-Detection-Platform
```

### 2. Create and Activate the Python Environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Backend Dependencies

```powershell
pip install pandas numpy scikit-learn matplotlib joblib
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv python-multipart PyJWT
```

### 4. Start the Backend

From the project root:

```powershell
uvicorn backend.app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Install Frontend Dependencies

Open a second terminal:

```powershell
cd frontend
npm install
```

### 6. Start the Frontend

```powershell
npm run dev
```

Open the URL shown in the terminal, usually:

```text
http://localhost:5173
```

## Demo Login

For local development:

```text
Username: admin
Password: admin123
```

## Example Transaction

Use the Swagger documentation at `/docs` and send a request to `POST /transactions/`:

```json
{
  "transaction_id": "TXN1000",
  "user_id": "USER1000",
  "amount": 25000,
  "merchant": "Amazon",
  "location": "Mumbai",
  "device_id": "DEVICE_NEW_1000",
  "timestamp": "2026-09-11T02:30:00",
  "previous_transactions": 1,
  "is_new_device": 1,
  "distance_from_previous": 800,
  "is_night": 1
}
```

The response contains:

- Machine learning score
- Anomaly score
- Rule score
- Final risk score
- Risk level
- Human-readable fraud reasons

Each `transaction_id` must be unique.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/auth/login` | Analyst login |
| POST | `/transactions/` | Create and score transaction |
| GET | `/transactions/` | Get transactions |
| POST | `/analysts/transactions/{id}/decision` | Approve or reject transaction |
| GET | `/analysts/audit-logs` | Get audit logs |
| GET | `/analytics/summary` | Get dashboard analytics |
| GET | `/analytics/performance` | Get model performance |
| GET | `/monitoring/drift` | Get drift-monitoring information |

## Future Improvements

- PostgreSQL production database
- Docker-based deployment
- Cloud deployment
- WebSocket-based live transaction updates
- Improved fraud-class precision
- More realistic production datasets
- Automated model retraining
- Advanced geographic and impossible-travel detection
- Stronger role-based permissions
- Unit and integration test coverage
- CI/CD pipeline

## Disclaimer

This project is an educational and portfolio demonstration. It uses generated transaction data and should not be used as a production financial fraud-detection system without further validation, security review, monitoring, and compliance testing.

## Author

**Harsh Singh Baghel**

- GitHub: https://github.com/tourtrial05-stack
- Project: https://github.com/tourtrial05-stack/Fraud-Detection-Platform