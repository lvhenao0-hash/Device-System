# app/routes/user_routes.py
<<<<<<< HEAD
=======
# Endpoints del recurso "users": listar, consultar por id, filtrar, crear,
# actualizar (completo y parcial) y eliminar.
#
# A partir de la Fase 2 de la actividad, la lógica de negocio se movió a
# app/services/user_service.py y los datos en memoria a app/data/users_db.py,
# para separar responsabilidades. Las rutas ahora se apoyan en dependencias
# reutilizables (Depends) definidas en app/dependencies/user_dependencies.py.

>>>>>>> a0aa56d0e8304b04ff5cea7ad42de91ffb0e6069
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dependencies.user_dependencies import get_user_or_404
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserUpdate
from app.services import user_service

<<<<<<< HEAD
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse], summary="Listar usuarios")
def listar_usuarios(
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
=======
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
>>>>>>> a0aa56d0e8304b04ff5cea7ad42de91ffb0e6069
):
    return user_service.listar_usuarios(role=role, is_active=is_active)


<<<<<<< HEAD
@router.get("/{user_id}", response_model=UserResponse, summary="Consultar un usuario")
def obtener_usuario(usuario: dict = Depends(get_user_or_404)):
    return usuario


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Registrar un usuario")
def crear_usuario(usuario: UserCreate):
    if user_service.correo_ya_existe(usuario.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {usuario.email}")
    return user_service.crear_usuario(usuario.model_dump())


@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar un usuario (completo)")
def actualizar_usuario(datos: UserUpdate, usuario_existente: dict = Depends(get_user_or_404)):
    if user_service.correo_ya_existe(datos.email, excluir_id=usuario_existente["id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {datos.email}")
    return user_service.actualizar_usuario_completo(usuario_existente["id"], datos.model_dump())


@router.patch("/{user_id}", response_model=UserResponse, summary="Actualizar un usuario (parcial)")
def actualizar_usuario_parcial(datos: UserPatch, usuario_existente: dict = Depends(get_user_or_404)):
    campos_enviados = datos.model_dump(exclude_unset=True)
    if not campos_enviados:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes enviar al menos un campo para actualizar")
    if "email" in campos_enviados and user_service.correo_ya_existe(campos_enviados["email"], excluir_id=usuario_existente["id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {campos_enviados['email']}")
    return user_service.actualizar_usuario_parcial(usuario_existente["id"], campos_enviados)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, summary="Eliminar un usuario")
def eliminar_usuario(usuario_existente: dict = Depends(get_user_or_404)):
    user_service.eliminar_usuario(usuario_existente["id"])
    return {"detail": f"Usuario con id {usuario_existente['id']} eliminado correctamente"}
=======
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
>>>>>>> a0aa56d0e8304b04ff5cea7ad42de91ffb0e6069
