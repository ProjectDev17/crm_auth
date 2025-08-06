import json
from services.auth_service import authenticate

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return _response(400, {"message": "Email y password son requeridos"})

    auth = authenticate(email, password)
    if not auth:
        return _response(401, {"message": "Credenciales inválidas"})

    return _response(200, auth)

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
