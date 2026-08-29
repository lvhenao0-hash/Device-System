from typing import Literal
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


class UserResponse(UserBase):
    """Modelo de SALIDA: lo que la API devuelve (incluye el id generado)."""

    id: int = Field(..., description="Identificador único del usuario")

    class Config:
        from_attributes = True