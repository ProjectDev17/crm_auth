import json
from services.auth_service import send_password_reset

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    email = body.get("email")
    if not email:
        return _res(400, {"message": "Email es requerido"})

    ok = send_password_reset(email)
    if not ok:
        return _res(404, {"message": "Usuario no encontrado"})

    return _res(200, {"message": "Email de recuperación enviado"})

def _res(code, body):
    return {"statusCode": code, "body": json.dumps(body)}
