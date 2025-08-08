import sys; sys.path.append('/opt')  # <--- ¡Esta línea hace que la layer esté disponible en todo el proceso!

import os
import json

# Handlers públicos
from handlers_public.login_post import lambda_handler as login_handler
from handlers_public.forgot_password_post import lambda_handler as forgot_password_handler
from handlers_public.refresh_token_post import lambda_handler as refresh_token_handler
from handlers_public.register_post import lambda_handler as register_handler
from handlers_public.validate_token_post import lambda_handler as validate_token_handler
from handlers_public.send_validation_email_post import lambda_handler as send_validation_email_handler
from handlers_public.validate_email_post import lambda_handler as validate_email_handler

def lambda_handler(event, context):
    db_name = os.getenv("MONGODB_DB_NAME")
    if not db_name:
        return _response(500, {"error": "No se encontró la variable de entorno MONGODB_DB_NAME"})

    event["db_name"] = db_name

    method = _get_http_method(event)
    path = _get_path(event)

    try:
        print(f"Processing {method} request for {path}")
        if method == "POST":
            if path == "/login":
                return login_handler(event, context)
            elif path == "/forgot-password":
                return forgot_password_handler(event, context)
            elif path == "/refresh-token":
                return refresh_token_handler(event, context)
            elif path == "/register":
                return register_handler(event, context)
            elif path == "/validate-token":
                return validate_token_handler(event, context)
            elif path == "/logout":
                return logout_handler(event, context)
            elif path == "/send-validation-email":
                return send_validation_email_handler(event, context)
            elif path == "/validate-email":
                return validate_email_handler(event, context)
        return _response(405, {"error": f"Método {method} no soportado para {path}"})

    except Exception as e:
        return _response(500, {"error": str(e)})

# Helpers
def _get_http_method(event):
    m = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "")
    return m.upper()

def _get_path(event):
    return event.get("path") or event.get("rawPath") or event.get("requestContext", {}).get("http", {}).get("path", "")

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
