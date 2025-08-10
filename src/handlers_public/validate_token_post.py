import sys
sys.path.append('/opt')

import json
from services.db import get_database
from utils.timestamp import now_ts  # debe retornar epoch en segundos

def lambda_handler(event, context):
    db_name = event["db_name"]
    db = get_database(db_name)
    users = db["users"]

    try:
        # 1) Obtener token desde body o header (Authorization: Bearer <token>)
        token = None

        # Body
        if event.get("body"):
            try:
                body = json.loads(event["body"])
                token = body.get("token")
            except json.JSONDecodeError:
                pass

        # Header
        if not token:
            auth_header = (event.get("headers") or {}).get("Authorization") or (event.get("headers") or {}).get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return _res(400, {"valid": False, "message": "Token no proporcionado"})

        # 2) Buscar usuario por validation_token
        user = users.find_one({"validation_token": token})
        if not user:
            return _res(404, {"valid": False, "message": "Token inválido o no encontrado"})

        now = now_ts()
        expires = user.get("validation_token_expires")

        # 3) Validar expiración
        if not isinstance(expires, (int, float)) or int(expires) <= now:
            return _res(410, {"valid": False, "message": "Token expirado"})

        # 4) Marcar como verificado y limpiar token
        users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "email_verified": True,
                    "email_verified_at": now
                },
                "$unset": {
                    "validation_token": "",
                    "validation_token_expires": "",
                    "validation_token_sent_at": ""
                }
            }
        )

        # 5) Respuesta exitosa
        return _res(200, {
            "valid": True,
            "message": "Email verificado correctamente",
            "email": user.get("email")
        })

    except Exception as e:
        return _res(500, {"valid": False, "message": str(e)})


def _res(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
