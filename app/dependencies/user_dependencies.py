# app/dependencies/user_dependencies.py
# Dependencias reutilizables (Dependency Injection) para el recurso "users".
# Se inyectan en las rutas mediante Depends(), evitando duplicar lógica
# común como la búsqueda de un usuario por ID o la validación de correo.

from fastapi import HTTPException, status

from app.services import user_service
from app.schemas.user_schema import UserCreate, UserUpdate, UserPartialUpdate


def obtener_usuario_o_404(user_id: int) -> dict:
    """
    Busca un usuario por ID. Si no existe, lanza un HTTPException 404.
    Se usa en GET por ID, PUT, PATCH y DELETE.
    """
    usuario = user_service.buscar_usuario(user_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un usuario con id {user_id}",
        )
    return usuario


def validar_correo_no_duplicado_creacion(datos: UserCreate) -> UserCreate:
    """
    Valida que el correo enviado al crear un usuario no exista ya en la
    base de datos. Se usa en POST /users.
    """
    if user_service.correo_existe(datos.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario registrado con el correo {datos.email}",
        )
    return datos


def validar_correo_no_duplicado_actualizacion(user_id: int, datos: UserUpdate) -> UserUpdate:
    """
    Valida que el correo enviado en un PUT no pertenezca a otro usuario
    distinto del que se está actualizando.
    """
    if user_service.correo_existe(datos.email, excluir_user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe otro usuario registrado con el correo {datos.email}",
        )
    return datos


def validar_patch_no_vacio(datos: UserPartialUpdate) -> UserPartialUpdate:
    """
    Valida que el body de un PATCH no venga vacío.
    Se usa en PATCH /users/{user_id}.
    """
    campos_enviados = datos.model_dump(exclude_unset=True)
    if not campos_enviados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )
    return datos


def validar_correo_patch_no_duplicado(user_id: int, datos: UserPartialUpdate) -> UserPartialUpdate:
    """
    Si el PATCH incluye un nuevo correo, valida que no pertenezca a otro
    usuario distinto del que se está actualizando.
    """
    if datos.email is not None and user_service.correo_existe(datos.email, excluir_user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe otro usuario registrado con el correo {datos.email}",
        )
    return datos


def obtener_configuracion_api() -> dict:
    """
    Dependencia de ejemplo que simula la obtención de configuración
    general de la API (nombre de la app, versión, etc.).
    """
    return {"app_name": "device_systems", "version": "2.0"}
