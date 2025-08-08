# handlers_public/logout_post.py

import json

def lambda_handler(event, context):
    # Simplemente responde éxito; el frontend debe eliminar el token guardado.
    return _response(200, {"message": "Logout exitoso. Token eliminado en cliente."})

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
