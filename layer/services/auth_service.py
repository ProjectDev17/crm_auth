# python/services/auth_service.py
import os
import bcrypt
import time
from typing import Optional, Dict
from services.db import get_mongo_client
from utils.hash_password import verify_password  # Usa tu función de la layer
from utils.jwt_token import generate_jwt, generate_jwt_refresh, decode_jwt  # Usa tu función de la layer

def _get_user_collection(db_name):
    client = get_mongo_client()
    return client[db_name]["users"]

def hash_password(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt())

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
    refresh_token = generate_jwt_refresh(str(user["_id"]), email)

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
    
    print(f"Enviando email de recuperación a {email}")
    return True

def refresh_access_token(refresh_token: str):
    if refresh_token == "":
        return None
    decoded = decode_jwt(refresh_token)
    if not decoded:
        return None
    access_token = generate_jwt(decoded["user_id"], decoded["email"])
    refresh_token = generate_jwt_refresh(decoded["user_id"], decoded["email"])
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "_id": decoded["user_id"],
            "email": decoded["email"]
        }
    }
