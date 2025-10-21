import os
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_super_secret_key_for_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
USERS_DB_PATH = "users.json"

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """Decodes the JWT token and returns the username (subject)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def read_users_db() -> Dict[str, Any]:
    """Reads the entire user database from the JSON file."""
    if not os.path.exists(USERS_DB_PATH):
        return {}
    with open(USERS_DB_PATH, "r") as f:
        return json.load(f)


def write_users_db(data: Dict[str, Any]):
    """Writes the entire user database to the JSON file."""
    with open(USERS_DB_PATH, "w") as f:
        json.dump(data, f, indent=2)
