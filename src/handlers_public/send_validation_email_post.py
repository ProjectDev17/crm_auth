import json
import uuid
import datetime
from services.db import get_database
from utils.send_email import send_validation_email

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

        # Generar token y fecha de expiración
        token = str(uuid.uuid4())
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        # Guardar el token temporal en el usuario
        users.update_one(
            {"email": email},
            {"$set": {
                "validation_token": token,
                "validation_token_expires": expires
            }}
        )

        # Envía el correo (implementar en producción)
        message=send_validation_email(email, token)

        return _response(200, {"message": message})
    except Exception as e:
        return _response(500, {"error": str(e)})

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
