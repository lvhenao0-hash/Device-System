"""Utilidad de un solo uso: asigna una contrasena (hasheada) a un usuario
existente que aun no tenga hashed_password, para poder iniciar sesion.
Uso: python crear_password_admin.py
"""

from app.auth.security import get_password_hash
from app.database.connection import SessionLocal
from app.models.user_model import User

EMAIL_OBJETIVO = "camila@correo.com"
PASSWORD_NUEVA = "Admin123!"

db = SessionLocal()
try:
    usuario = db.query(User).filter(User.email == EMAIL_OBJETIVO).first()
    if usuario:
        usuario.hashed_password = get_password_hash(PASSWORD_NUEVA)
        db.commit()
        print(f"Contrasena actualizada para {EMAIL_OBJETIVO}")
    else:
        print(f"Usuario {EMAIL_OBJETIVO} no encontrado")
finally:
    db.close()
