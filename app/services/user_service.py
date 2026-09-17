# app/services/user_service.py
# Lógica de negocio del recurso "users". Las rutas delegan aquí en lugar
# de manipular usuarios_db directamente (Fase 2: separación de responsabilidades).

from typing import Optional, List

from app.data.users_db import usuarios_db, obtener_siguiente_id
from app.schemas.user_schema import UserCreate, UserUpdate, UserPartialUpdate


def listar_usuarios(role: Optional[str] = None, is_active: Optional[bool] = None) -> List[dict]:
    """Lista usuarios, permitiendo filtrar opcionalmente por rol y/o estado."""
    resultado = usuarios_db

    if role is not None:
        resultado = [u for u in resultado if u["role"] == role]

    if is_active is not None:
        resultado = [u for u in resultado if u["is_active"] == is_active]

    return resultado


def buscar_usuario(user_id: int) -> Optional[dict]:
    """Busca un usuario por su ID. Devuelve None si no existe."""
    for usuario in usuarios_db:
        if usuario["id"] == user_id:
            return usuario
    return None


def correo_existe(email: str, excluir_user_id: Optional[int] = None) -> bool:
    """Valida si un correo ya está registrado por otro usuario."""
    return any(
        u["email"] == email and u["id"] != excluir_user_id
        for u in usuarios_db
    )


def crear_usuario(datos: UserCreate) -> dict:
    """Crea un nuevo usuario y lo agrega a la base de datos en memoria."""
    nuevo_usuario = datos.model_dump()
    nuevo_usuario["id"] = obtener_siguiente_id()
    usuarios_db.append(nuevo_usuario)
    return nuevo_usuario


def reemplazar_usuario(user_id: int, datos: UserUpdate) -> dict:
    """Reemplaza por completo la información de un usuario existente (PUT)."""
    usuario = buscar_usuario(user_id)
    actualizado = datos.model_dump()
    actualizado["id"] = user_id
    usuario.update(actualizado)
    return usuario


def actualizar_usuario_parcial(user_id: int, datos: UserPartialUpdate) -> dict:
    """Actualiza solo los campos enviados de un usuario existente (PATCH)."""
    usuario = buscar_usuario(user_id)
    campos_enviados = datos.model_dump(exclude_unset=True)
    usuario.update(campos_enviados)
    return usuario


def eliminar_usuario(user_id: int) -> None:
    """Elimina un usuario existente de la base de datos en memoria."""
    usuario = buscar_usuario(user_id)
    usuarios_db.remove(usuario)
