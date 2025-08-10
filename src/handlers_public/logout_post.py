# handlers_public/logout_post.py

import json
from services.db import get_database

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    db_name = event["db_name"]
    access_token = body.get("access_token")
    if not access_token:
        return _res(400, {"message": "Access token es requerido"})
    
    db = get_database(db_name)
    collection = db["users"]
    
    # Eliminar el access_token y refresh_token de la base de datos
    collection.update_one({"access_token": access_token}, {"$unset": {"access_token": "", "refresh_token": ""}})

    return _res(200, {"message": "Logout exitoso. Token eliminado en cliente."})

def _res(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
