# app/data/users_db.py
# Simulación de base de datos en memoria para el recurso "users".
# Se extrae de user_routes.py (Fase 1) para separar responsabilidades,
# siguiendo la estructura solicitada en la Fase 2 de la actividad.

usuarios_db = [
    {"id": 1, "name": "Laura Arias", "email": "laura@correo.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Leo Carmona", "email": "leo@correo.com", "role": "user", "is_active": True},
    {"id": 3, "name": "Sebastian Lozano", "email": "sebastian@correo.com", "role": "support", "is_active": False},
]

contador_id = 4


def obtener_siguiente_id() -> int:
    """Genera y reserva el siguiente ID disponible para un nuevo usuario."""
    global contador_id
    nuevo_id = contador_id
    contador_id += 1
    return nuevo_id
