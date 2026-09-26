from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Literal["admin", "support", "user"] = "user"

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        if any(ch.isspace() for ch in value):
            raise ValueError("La contrasena no puede contener espacios")
        if not any(ch.isupper() for ch in value):
            raise ValueError("La contrasena debe tener al menos una mayuscula")
        if not any(ch.islower() for ch in value):
            raise ValueError("La contrasena debe tener al menos una minuscula")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("La contrasena debe tener al menos un numero")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int
    email: EmailStr
    role: Literal["admin", "support", "user"]


class AuthUserResponse(BaseModel):
    """Respuesta publica del usuario autenticado. Nunca incluye hashed_password."""

    id: int
    name: str
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
