import sys
sys.path.append('/opt')

import os
import json
import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def lambda_handler(event, context):
    try:
        # 1. Obtener token desde body o header
        token = None

        # Body
        if event.get("body"):
            try:
                body = json.loads(event["body"])
                token = body.get("token")
            except json.JSONDecodeError:
                pass

        # Header Authorization: Bearer <token>
        if not token:
            auth_header = event.get("headers", {}).get("Authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]

        if not token:
            return _res(400, {"valid": False, "message": "Token no proporcionado"})

        # 2. Decodificar y validar
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # 3. Respuesta exitosa
        return _res(200, {
            "valid": True,
            "message": "Token válido",
            "payload": payload
        })

    except jwt.ExpiredSignatureError:
        return _res(401, {"valid": False, "message": "Token expirado"})
    except jwt.InvalidTokenError:
        return _res(401, {"valid": False, "message": "Token inválido"})
    except Exception as e:
        return _res(500, {"valid": False, "message": str(e)})

def _res(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
