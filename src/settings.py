# src/settings.py

"""
Aquí definimos los permisos requeridos para cada recurso y verbo HTTP.
Puedes ajustar este diccionario según las necesidades de tu aplicación.
"""

PERMISSION_REQUIRED = {
    # Recurso “auth”:
    "auth": {
        "GET":    ["read:auth"],
        "POST":   ["create:auth"],
        "PUT":    ["update:auth"]
    },
}
