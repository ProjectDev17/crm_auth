import sys
sys.path.append('/opt')

import json
from services.auth_service import send_password_reset

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    email = body.get("email")
    db_name = event["db_name"]
    if not email:
        return _res(400, {"message": "Email es requerido"})
    title = "Restablecer contraseña"
    body = f"Haz clic en el siguiente enlace para restablecer tu contraseña: https://app.digitalcrm.net/reset-password?token={new_token}"

    ok = send_password_reset(email, db_name, title, body)
    if not ok:
        return _res(404, {"message": "Usuario no encontrado"})

    return _res(200, {"message": "Email de recuperación enviado"})

def _res(code, body):
    return {"statusCode": code, "body": json.dumps(body)}
