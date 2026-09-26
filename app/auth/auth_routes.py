"""Endpoints de autenticacion exigidos por EV11: /auth/register, /auth/login,
/auth/me. OAuth2PasswordRequestForm usa el campo "username" del formulario
para transportar el email (asi lo espera Swagger con OAuth2)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import auth_service
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.middlewares.rate_limiter import limiter
from app.models.user_model import User
from app.schemas.auth_schema import AuthUserResponse, Token, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un usuario nuevo",
)
@limiter.limit("3/minute")
def register(datos: UserRegister, request: Request, db: Session = Depends(get_db)):
    usuario = auth_service.registrar_usuario(db, datos)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya esta registrado",
        )
    return usuario


@router.post("/login", response_model=Token, summary="Iniciar sesion y obtener un token JWT")
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = auth_service.autenticar_usuario(db, form_data.username, form_data.password)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_service.generar_token(usuario)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=AuthUserResponse, summary="Usuario autenticado actual")
def me(current_user: User = Depends(get_current_active_user)):
    return current_user
