from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electronico unico del usuario")
    role: Literal["admin", "support", "user"] = Field(..., description="Rol del usuario en el sistema")
    is_active: bool = Field(default=True, description="Indica si el usuario esta activo")


class UserCreate(UserBase):
    """Entrada para POST /users (creacion administrativa). Requiere una
    contrasena inicial que se almacena como hash, igual que en /auth/register."""
    password: str = Field(..., min_length=8, description="Contrasena inicial del usuario (se guarda como hash)")


class UserUpdate(UserBase):
    """Entrada para PUT /users/{user_id}: reemplazo completo."""
    pass


class UserPatch(BaseModel):
    """Entrada para PATCH /users/{user_id}: actualizacion parcial, todo opcional."""
    name: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = Field(None)
    role: Optional[Literal["admin", "support", "user"]] = Field(None)
    is_active: Optional[bool] = Field(None)


class UserResponse(UserBase):
    """Salida: incluye datos que genera la base de datos."""
    id: int = Field(..., description="Identificador unico del usuario")
    created_at: datetime = Field(..., description="Fecha y hora de creacion")

    model_config = ConfigDict(from_attributes=True)