import json
import uuid
from services.db import get_database
from utils.send_email import send_validation_email
from utils.timestamp import add_hours_to_timestamp, now_ts  # epoch (s)
# Reglas:
# - No enviar email si no han pasado 15 min desde el último envío
# - Si ya pasaron 15 min y existe un token vigente, devolverlo y reenviar
# - Si ya pasaron 15 min y no hay token vigente, generar uno nuevo y enviar

FIFTEEN_MIN_SECS = 15 * 60

def lambda_handler(event, context):
    db_name = event["db_name"]
    db = get_database(db_name)
    users = db["users"]

    try:
        data = json.loads(event["body"])
        email = data.get("email")

        if not email:
            return _response(400, {"error": "Email requerido"})

        user = users.find_one({"email": email})
        if not user:
            return _response(404, {"error": "Usuario no encontrado"})

        now = now_ts()

        # Si tienes email_verified_at y fue hace <15 min, bloquea
        email_verified_at = user.get("email_verified_at")
        if isinstance(email_verified_at, (int, float)):
            elapsed_since_verify = now - int(email_verified_at)
            if elapsed_since_verify < FIFTEEN_MIN_SECS:
                return _response(409, {
                    "error": "El email fue verificado recientemente.",
                    "retry_in_seconds": FIFTEEN_MIN_SECS - elapsed_since_verify
                })

        # Cooldown de envío
        last_sent = user.get("validation_token_sent_at")
        if isinstance(last_sent, (int, float)):
            elapsed = now - int(last_sent)
            if elapsed < FIFTEEN_MIN_SECS:
                # ⛔ NO enviar email ni actualizar campos si estás en cooldown
                return _response(429, {
                    "error": "Debes esperar 15 minutos entre envíos.",
                    "retry_in_seconds": FIFTEEN_MIN_SECS - elapsed
                })

        # Pasó el cooldown -> ¿hay token vigente?
        existing_token = user.get("validation_token")
        token_expires = user.get("validation_token_expires")
        token_is_valid = (
            isinstance(existing_token, str)
            and isinstance(token_expires, (int, float))
            and int(token_expires) > now
        )

        if token_is_valid:
            # Reutiliza token vigente y ENVÍA email (ya pasó cooldown)
            users.update_one(
                {"email": email},
                {"$set": {"validation_token_sent_at": now}}
            )
            message = send_validation_email(email, existing_token)
            return _response(200, {
                "message": message,
                "reused": True,
                "expires_at": int(token_expires)
            })

        # No hay token vigente -> generar uno nuevo y ENVÍAR email
        new_token = str(uuid.uuid4())
        users.update_one(
            {"email": email},
            {"$set": {
                "validation_token": new_token,
                "validation_token_expires": add_hours_to_timestamp(1),  # 1h
                "validation_token_sent_at": now
            }}
        )
        frontend_url = "https://app.digitalcrm.net"
        """
        Envía el email de validación al usuario usando SMTP de Gmail.
        """
        validation_link = f"{frontend_url}/validate-email?token={token}"
        
        subject = "Valida tu cuenta"
        body = f"""Hola,
            Para validar tu cuenta, haz clic en el siguiente enlace:
            {validation_link}

            Si no solicitaste este registro, puedes ignorar este mensaje.
        """

        message = send_validation_email(email, new_token, subject, body)
        return _response(200, {
            "message": message,
            "reused": False
        })

    except Exception as e:
        return _response(500, {"error": str(e)})

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
