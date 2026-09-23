from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import get_user_or_404
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse], summary="Listar usuarios")
def listar_usuarios(
    role: Optional[str] = Query(None, description="Filtrar por rol: admin, support o user"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    order_by: Optional[str] = Query(None, description="Ordenar por: name o created_at"),
    db: Session = Depends(get_db),
):
    return user_service.listar_usuarios(db, role=role, is_active=is_active, order_by=order_by)


@router.get("/{user_id}", response_model=UserResponse, summary="Consultar un usuario")
def obtener_usuario(usuario: User = Depends(get_user_or_404)):
    return usuario


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Registrar un usuario")
def crear_usuario(usuario: UserCreate, db: Session = Depends(get_db)):
    if user_service.buscar_usuario_por_email(db, usuario.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {usuario.email}")
    return user_service.crear_usuario(db, usuario.model_dump())


@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar un usuario (completo)")
def actualizar_usuario(datos: UserUpdate, usuario_existente: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    otro = user_service.buscar_usuario_por_email(db, datos.email)
    if otro and otro.id != usuario_existente.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {datos.email}")
    return user_service.actualizar_usuario_completo(db, usuario_existente, datos.model_dump())


@router.patch("/{user_id}", response_model=UserResponse, summary="Actualizar un usuario (parcial)")
def actualizar_usuario_parcial(datos: UserPatch, usuario_existente: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    campos = datos.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes enviar al menos un campo para actualizar")
    if "email" in campos:
        otro = user_service.buscar_usuario_por_email(db, campos["email"])
        if otro and otro.id != usuario_existente.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {campos['email']}")
    return user_service.actualizar_usuario_parcial(db, usuario_existente, campos)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, summary="Eliminar un usuario")
def eliminar_usuario(usuario_existente: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    user_service.eliminar_usuario(db, usuario_existente)
    return {"detail": f"Usuario con id {usuario_existente.id} eliminado correctamente"}