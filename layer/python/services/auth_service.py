import os
import bcrypt
import jwt
import time
from typing import Optional, Dict
from utils.db import get_mongo_client

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")     # usa Secrets Manager
JWT_EXP_SECS = int(os.getenv("JWT_EXP_SECS", "3600"))  # 1 h por defecto

def _get_user_collection():
    client = get_mongo_client()
    return client["crm"]["users"]  # ajusta a tu DB + colección

def hash_password(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt())

def verify_password(plain: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed)

def generate_jwt(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP_SECS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def authenticate(email: str, password: str) -> Optional[Dict]:
    """Devuelve dict con usuario + token o None."""
    user = _get_user_collection().find_one({"email": email, "status": True})
    if not user or not verify_password(password, user["password"]):
        return None
    token = generate_jwt(str(user["_id"]), email)
    return {"token": token, "user": {"_id": str(user['_id']), "email": email}}
