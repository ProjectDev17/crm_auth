import jwt
import os
from datetime import now_ts, add_hours_to_timestamp

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")     # usa Secrets Manager
JWT_EXP_SECS = int(os.getenv("JWT_EXP_SECS", "3600"))  # 1 h por defecto

def generate_jwt(user_id: str, email: str) -> str:
    JWT_EXP_HOURS = JWT_EXP_SECS/3600
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": now_ts,
        "exp": add_hours_to_timestamp(now_ts, JWT_EXP_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def generate_jwt_refresh(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": now_ts,
        "exp": add_hours_to_timestamp(now_ts, 1),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
