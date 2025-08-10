import sys
sys.path.append('/opt')

import json
from services.auth_service import authenticate

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    email = body.get("email")
    password = body.get("password")
    db_name = event["db_name"]

    if not email or not password:
        return _res(400, {"message": "Email y password son requeridos"})

    auth_data = authenticate(email, password, db_name)
    if not auth_data:
        return _res(401, {"message": "Credenciales inválidas"})

    return _res(200, {
        "access_token": auth_data["access_token"],
        "refresh_token": auth_data["refresh_token"],
        "user": auth_data["user"]
    })

def _res(code, body):
    return {"statusCode": code, "body": json.dumps(body)}
