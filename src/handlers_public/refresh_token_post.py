import sys
sys.path.append('/opt')

import json
from services.auth_service import refresh_access_token

def lambda_handler(event, context):
    
    body = json.loads(event.get("body") or "{}")
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        return _res(400, {"message": "Refresh token es requerido"})
    
    db_name = event["db_name"]
    if not db_name:
        return _res(400, {"message": "DB name es requerido"})
    
    db = get_database(db_name)
    collection = db["users"]
    
    # Verificar si existe el refresh_token
    if not collection.find_one({"refresh_token": refresh_token}):
        return _res(401, {"message": "Refresh token inválido"})

    data = refresh_access_token(refresh_token)
    if not data:
        return _res(401, {"message": "Refresh token inválido"})

    return _res(200, data)

def _res(code, body):
    return {"statusCode": code, "body": json.dumps(body)}
