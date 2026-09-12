import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.operations import Analyst


SECRET_KEY = "fraud-platform-dev-secret-change-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100_000
    )

    return f"{salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split("$")

        salt = bytes.fromhex(salt_hex)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            100_000
        )

        return secrets.compare_digest(
            password_hash.hex(),
            hash_hex
        )

    except Exception:
        return False


def create_access_token(username: str, role: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    user = (
        db.query(Analyst)
        .filter(Analyst.username == username)
        .first()
    )

    if not user or not user.is_active:
        raise credentials_exception

    return user


def ensure_default_users(db: Session):

    existing_admin = (
        db.query(Analyst)
        .filter(Analyst.username == "admin")
        .first()
    )

    if not existing_admin:
        db.add(
            Analyst(
                username="admin",
                full_name="System Administrator",
                role="ADMIN",
                password_hash=hash_password("admin123")
            )
        )

    existing_analyst = (
        db.query(Analyst)
        .filter(Analyst.username == "analyst")
        .first()
    )

    if not existing_analyst:
        db.add(
            Analyst(
                username="analyst",
                full_name="Fraud Analyst",
                role="ANALYST",
                password_hash=hash_password("analyst123")
            )
        )

    db.commit()