# app/routes/user_routes.py
# Endpoints del recurso "users": listar, consultar por id, filtrar, crear,
# actualizar (completo y parcial) y eliminar.
#
# A partir de la Fase 2 de la actividad, la lógica de negocio se movió a
# app/services/user_service.py y los datos en memoria a app/data/users_db.py,
# para separar responsabilidades. Las rutas ahora se apoyan en dependencias
# reutilizables (Depends) definidas en app/dependencies/user_dependencies.py.

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserPartialUpdate,
    UserResponse,
    MessageResponse,
)
from app.services import user_service
from app.dependencies.user_dependencies import (
    obtener_usuario_o_404,
    validar_correo_no_duplicado_creacion,
    validar_correo_no_duplicado_actualizacion,
    validar_correo_patch_no_duplicado,
    validar_patch_no_vacio,
    obtener_configuracion_api,
)

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get(
    "",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Devuelve el listado de usuarios. Permite filtrar opcionalmente por rol y/o estado activo.",
    response_description="Listado de usuarios registrados en el sistema.",
)
def listar_usuarios(
    role: Optional[str] = Query(None, description="Filtrar por rol: admin, support o user"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    settings: dict = Depends(obtener_configuracion_api),
):
    return user_service.listar_usuarios(role=role, is_active=is_active)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar usuario por ID",
    description="Devuelve la información de un usuario específico a partir de su ID.",
    response_description="Datos del usuario solicitado.",
)
def obtener_usuario(usuario: dict = Depends(obtener_usuario_o_404)):
    return usuario


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema. Valida que el correo no esté duplicado.",
    response_description="Usuario creado exitosamente.",
)
def crear_usuario(datos: UserCreate = Depends(validar_correo_no_duplicado_creacion)):
    return user_service.crear_usuario(datos)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario (completo)",
    description="Reemplaza por completo la información de un usuario existente. Requiere todos los campos.",
    response_description="Usuario actualizado exitosamente.",
)
def actualizar_usuario_completo(
    user_id: int,
    datos: UserUpdate,
    usuario_existente: dict = Depends(obtener_usuario_o_404),
    datos_validados: UserUpdate = Depends(validar_correo_no_duplicado_actualizacion),
):
    return user_service.reemplazar_usuario(user_id, datos)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario (parcial)",
    description="Actualiza solo los campos enviados por el cliente. Debe enviarse al menos un campo.",
    response_description="Usuario actualizado parcialmente.",
)
def actualizar_usuario_parcial(
    user_id: int,
    datos: UserPartialUpdate,
    usuario_existente: dict = Depends(obtener_usuario_o_404),
    datos_sin_vacio: UserPartialUpdate = Depends(validar_patch_no_vacio),
    datos_validados: UserPartialUpdate = Depends(validar_correo_patch_no_duplicado),
):
    return user_service.actualizar_usuario_parcial(user_id, datos)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario",
    description="Elimina un usuario existente del sistema a partir de su ID.",
    response_description="Confirmación de eliminación del usuario.",
)
def eliminar_usuario(user_id: int, usuario_existente: dict = Depends(obtener_usuario_o_404)):
    user_service.eliminar_usuario(user_id)
    return {"detail": f"Usuario con id {user_id} eliminado correctamente"}