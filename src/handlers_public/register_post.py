import json
from services.db import get_database
from utils.hash_password import hash_password
from utils.crud import build_new_item

def lambda_handler(event, context):
    db_name = event["db_name"]
    db = get_database(db_name)
    collection = db["users"]

    try:
        data = json.loads(event["body"])
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        full_name = data.get("full_name", "")
        # Validaciones básicas
        if not email or not username or not password:
            return _response(400, {"error": "Faltan campos obligatorios"})

        # Verificar si existe usuario
        if collection.find_one({"$or": [{"email": email}, {"username": username}]}):
            return _response(409, {"error": "El usuario o email ya existe"})

        # Crear usuario
        body = {
            "email": email,
            "username": username,
            "password": hash_password(password),
            "full_name": full_name,
            "email_verified": False
        }
        
        user = build_new_item(
            body=body,
            created_by_user=username
        )
        result = collection.insert_one(user)
        return _response(201, {"message": "Usuario creado correctamente", "user_id": str(result.inserted_id)})
    except Exception as e:
        return _response(500, {"error": str(e)})

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
