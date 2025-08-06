import os, jwt
from services.auth_service import JWT_SECRET

def lambda_handler(event, context):
    token = _extract_token(event)
    if not token:
        return _deny("missing")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        principal_id = payload["sub"]
        return _allow(principal_id, event["methodArn"])
    except jwt.ExpiredSignatureError:
        return _deny("expired")
    except jwt.InvalidTokenError:
        return _deny("invalid")

# helpers ----------------------------------------------------------
def _extract_token(event):
    auth = event["headers"].get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1]
    return None

def _policy(effect, principal_id, resource):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}
            ],
        },
    }

def _allow(principal_id, resource): return _policy("Allow", principal_id, resource)
def _deny(reason): return _policy("Deny", f"anon_{reason}", "*")
