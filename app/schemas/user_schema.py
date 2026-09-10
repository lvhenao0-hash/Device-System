from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Campos comunes a todo usuario, compartidos entre entrada y salida."""

    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electrónico único del usuario")
    role: Literal["admin", "support", "user"] = Field(..., description="Rol del usuario en el sistema")
    is_active: bool = Field(default=True, description="Indica si el usuario está activo")


class UserCreate(UserBase):
    """Modelo de ENTRADA: lo que se recibe en el body del POST /users."""
    pass


class UserUpdate(UserBase):
    """
    Modelo de ENTRADA para la actualización completa (PUT /users/{user_id}).
    Requiere todos los campos, ya que reemplaza por completo el recurso.
    """
    pass


class UserPartialUpdate(BaseModel):
    """
    Modelo de ENTRADA para la actualización parcial (PATCH /users/{user_id}).
    Todos los campos son opcionales: el cliente solo envía lo que desea modificar.
    """

    name: Optional[str] = Field(default=None, min_length=3, description="Nombre completo del usuario")
    email: Optional[EmailStr] = Field(default=None, description="Correo electrónico único del usuario")
    role: Optional[Literal["admin", "support", "user"]] = Field(default=None, description="Rol del usuario en el sistema")
    is_active: Optional[bool] = Field(default=None, description="Indica si el usuario está activo")


class UserResponse(UserBase):
    """Modelo de SALIDA: lo que la API devuelve (incluye el id generado)."""

    id: int = Field(..., description="Identificador único del usuario")

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Modelo de SALIDA genérico para mensajes de confirmación (ej. eliminación)."""

    detail: str