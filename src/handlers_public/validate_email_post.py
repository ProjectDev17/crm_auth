import json
import datetime
from services.db import get_database

def lambda_handler(event, context):
    db_name = event["db_name"]
    db = get_database(db_name)
    users = db["users"]

    try:
        data = json.loads(event["body"])
        token = data.get("token")
        if not token:
            return _response(400, {"error": "Token requerido"})

        user = users.find_one({
            "validation_token": token,
            "validation_token_expires": {"$gt": datetime.datetime.utcnow()}
        })

        if not user:
            return _response(400, {"error": "Token inválido o expirado"})

        # Marca como validado y elimina el token
        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"email_verified": True},
             "$unset": {"validation_token": "", "validation_token_expires": ""}}
        )

        return _response(200, {"message": "Email verificado correctamente"})
    except Exception as e:
        return _response(500, {"error": str(e)})

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
