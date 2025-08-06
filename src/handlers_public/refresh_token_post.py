import json
from services.auth_service import refresh_access_token

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        return _res(400, {"message": "Refresh token requerido"})

    new_access = refresh_access_token(refresh_token)
    if not new_access:
        return _res(401, {"message": "Refresh token inválido o expirado"})

    return _res(200, {"access_token": new_access})

def _res(code, body):
    return {"statusCode": code, "body": json.dumps(body)}
