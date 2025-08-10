# python/services/auth_service.py
import os
import bcrypt
import jwt
import time
from typing import Optional, Dict
from services.db import get_mongo_client
from utils.hash_password import verify_password  # Usa tu función de la layer

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")     # usa Secrets Manager
JWT_EXP_SECS = int(os.getenv("JWT_EXP_SECS", "3600"))  # 1 h por defecto

def _get_user_collection(db_name):
    client = get_mongo_client()
    return client[db_name]["users"]

def hash_password(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt())

def generate_jwt(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP_SECS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def authenticate(email: str, password: str, db_name: str) -> Optional[Dict]:
    """
    Devuelve dict con usuario + tokens o None si la autenticación falla.
    """
    user = _get_user_collection(db_name).find_one({"email": email, "status": True})
    if not user:
        return None

    hashed_password = user.get("password")
    if not hashed_password:
        return None

    # Asegura que hashed_password sea bytes antes de verificar
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")

    if not verify_password(password, hashed_password.decode("utf-8")):
        return None

    # Genera access_token y refresh_token
    access_token = generate_jwt(str(user["_id"]), email)
    refresh_token = "fake-refresh-token"  # Aquí pones la lógica real

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "_id": str(user['_id']),
            "email": email
        }
    }


def send_password_reset(email: str, db_name: str) -> bool:
    # Simulación: busca el usuario y "envía" un correo de recuperación
    user = _get_user_collection(db_name).find_one({"email": email, "status": True})
    if not user:
        return False
    # Aquí iría la lógica para enviar el correo (SMTP, SES, etc.)
    print(f"Enviando email de recuperación a {email}")
    return True

# Agrega esto en python/services/auth_service.py

def refresh_access_token(refresh_token: str):
    if refresh_token != "fake-refresh-token":
        return None
    access_token = generate_jwt("dummy_user_id", "test@example.com")
    return {
        "access_token": access_token,
        "user": {"_id": "dummy_user_id", "email": "test@example.com"}
    }
