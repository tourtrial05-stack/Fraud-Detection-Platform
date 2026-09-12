from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import engine, Base, SessionLocal

# Import models so SQLAlchemy creates all tables
from backend.app.models.transaction import Transaction
from backend.app.models.operations import Analyst, AuditLog, Feedback

from backend.app.api.transactions import router as transaction_router
from backend.app.api.auth import router as auth_router
from backend.app.api.analysts import router as analyst_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.monitoring import router as monitoring_router

from backend.app.core.security import ensure_default_users


Base.metadata.create_all(bind=engine)


# Create default analyst accounts
db = SessionLocal()

try:
    ensure_default_users(db)
finally:
    db.close()


app = FastAPI(
    title="AI Fraud Detection Platform",
    description="AI-powered fraud detection and fraud operations API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
   allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(transaction_router)
app.include_router(auth_router)
app.include_router(analyst_router)
app.include_router(analytics_router)
app.include_router(monitoring_router)


@app.get("/")
def root():
    return {
        "message": "AI Fraud Detection Platform API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }