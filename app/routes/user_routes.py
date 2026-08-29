# app/routes/user_routes.py
# Endpoints del recurso "users": listar, consultar por id, filtrar y crear

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.user_schema import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Usuarios"])

usuarios_db = [
    {"id": 1, "name": "Ana Torres", "email": "ana@correo.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Luis Ramirez", "email": "luis@correo.com", "role": "user", "is_active": True},
    {"id": 3, "name": "Camilo Sarrazola", "email": "camilo@correo.com", "role": "support", "is_active": False},
]

contador_id = 4


@router.get("", response_model=List[UserResponse])
def listar_usuarios(
    role: Optional[str] = Query(None, description="Filtrar por rol: admin, support o user"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
):
    resultado = usuarios_db

    if role is not None:
        resultado = [u for u in resultado if u["role"] == role]

    if is_active is not None:
        resultado = [u for u in resultado if u["is_active"] == is_active]

    return resultado


@router.get("/{user_id}", response_model=UserResponse)
def obtener_usuario(user_id: int):
    for usuario in usuarios_db:
        if usuario["id"] == user_id:
            return usuario

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe un usuario con id {user_id}",
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UserCreate):
    global contador_id

    correo_existente = any(u["email"] == usuario.email for u in usuarios_db)
    if correo_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario registrado con el correo {usuario.email}",
        )

    nuevo_usuario = usuario.model_dump()
    nuevo_usuario["id"] = contador_id
    contador_id += 1

    usuarios_db.append(nuevo_usuario)
    return nuevo_usuario