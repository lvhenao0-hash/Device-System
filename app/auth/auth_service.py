from sqlalchemy.orm import Session

from app.auth.security import create_access_token, get_password_hash, verify_password
from app.models.user_model import User
from app.services import user_service


def registrar_usuario(db: Session, datos) -> User | None:
    """Crea un usuario nuevo con contrasena hasheada.

    Devuelve None si el correo ya existe (el router traduce esto a 400).
    """
    if user_service.buscar_usuario_por_email(db, datos.email):
        return None

    usuario = User(
        name=datos.name,
        email=datos.email,
        hashed_password=get_password_hash(datos.password),
        role=datos.role,
        is_active=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar_usuario(db: Session, email: str, password: str) -> User | None:
    """Verifica credenciales. Devuelve el usuario o None."""
    usuario = user_service.buscar_usuario_por_email(db, email)

    if not usuario:
        return None
    if not verify_password(password, usuario.hashed_password):
        return None
    if not usuario.is_active:
        return None

    return usuario


def generar_token(usuario: User) -> str:
    return create_access_token(
        {
            "sub": str(usuario.id),
            "email": usuario.email,
            "role": usuario.role,
        }
    )
