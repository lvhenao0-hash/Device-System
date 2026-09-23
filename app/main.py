from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, FastAPI, Path, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# =============================================================================
# 1. ERRORES DE NEGOCIO
#    Se lanzan desde el service y un único handler los convierte en JSON con
#    el mismo formato que usa FastAPI: {"detail": "..."}
# =============================================================================


class AppError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class BadRequestError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT


class ErrorResponse(BaseModel):
    """Formato de error, usado para documentar las respuestas en Swagger."""

    detail: str = Field(examples=["Mensaje descriptivo del error"])


class MessageResponse(BaseModel):
    """Respuesta de éxito con un mensaje (por ejemplo, al eliminar un usuario)."""

    detail: str = Field(examples=["Usuario con id 1 eliminado correctamente"])


R_404 = {404: {"model": ErrorResponse, "description": "Recurso no encontrado"}}
R_409 = {409: {"model": ErrorResponse, "description": "Conflicto: número de serie duplicado"}}

# =============================================================================
# 2. SCHEMAS (validación de entrada y forma de la salida)
#    Si el body no cumple las reglas, FastAPI responde 422 automáticamente.
# =============================================================================

SystemType = Literal["linux", "windows", "android", "ios", "embedded"]
UserRole = Literal["user", "admin", "support"]


class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


# ---- Users ------------------------------------------------------------------


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = "user"
    is_active: bool = True

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Carlos Gómez",
                "email": "carlos@correo.com",
                "role": "user",
                "is_active": True,
            }
        }
    )


class UserReplace(BaseModel):
    """Reemplazo completo (PUT): TODOS los campos son obligatorios."""

    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Luis Ramirez G.",
                "email": "luisg@correo.com",
                "role": "admin",
                "is_active": False,
            }
        }
    )


class UserUpdate(BaseModel):
    """Actualización parcial (PATCH): solo se envían los campos a cambiar."""

    name: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None

    model_config = ConfigDict(json_schema_extra={"example": {"role": "support"}})


class UserOut(BaseModel):
    name: str
    email: str
    role: str
    is_active: bool
    id: int


# ---- Device systems ---------------------------------------------------------


class DeviceSystemBase(BaseModel):
    name: str = Field(min_length=3, max_length=80, description="Nombre del dispositivo")
    serial_number: str = Field(
        min_length=5,
        max_length=40,
        pattern=r"^[A-Za-z0-9-]+$",
        description="Número de serie único (letras, números y guiones)",
    )
    system_type: SystemType = Field(description="Sistema operativo / tipo de sistema")
    version: str = Field(default="1.0.0", max_length=20, description="Versión del sistema")
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE, description="Estado actual")
    owner_id: int | None = Field(default=None, ge=1, description="ID del usuario propietario")
    description: str | None = Field(default=None, max_length=255)


class DeviceSystemCreate(DeviceSystemBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Sensor Bodega Norte",
                "serial_number": "SN-2024-0042",
                "system_type": "embedded",
                "version": "2.3.1",
                "status": "active",
                "owner_id": 1,
                "description": "Sensor de temperatura de la bodega",
            }
        }
    )


class DeviceSystemUpdate(BaseModel):
    """Actualización parcial (PATCH): solo se envían los campos a cambiar."""

    name: str | None = Field(default=None, min_length=3, max_length=80)
    serial_number: str | None = Field(
        default=None, min_length=5, max_length=40, pattern=r"^[A-Za-z0-9-]+$"
    )
    system_type: SystemType | None = None
    version: str | None = Field(default=None, max_length=20)
    status: DeviceStatus | None = None
    owner_id: int | None = Field(default=None, ge=1)
    description: str | None = Field(default=None, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={"example": {"status": "maintenance", "version": "2.4.0"}}
    )


class DeviceSystemOut(DeviceSystemBase):
    id: int
    created_at: datetime
    updated_at: datetime


# =============================================================================
# 3. REPOSITORIOS (capa de datos; aquí en memoria, luego puede ser una BD real)
# =============================================================================


def _now() -> datetime:
    return datetime.now(timezone.utc)


class UserRepository:
    def __init__(self) -> None:
        self._items: dict[int, dict] = {}
        self._next_id = 1

    def list_all(self) -> list[dict]:
        return list(self._items.values())

    def get(self, user_id: int) -> dict | None:
        return self._items.get(user_id)

    def get_by_email(self, email: str) -> dict | None:
        return next((u for u in self._items.values() if u["email"].lower() == email.lower()), None)

    def create(self, data: dict) -> dict:
        user = {"id": self._next_id, **data}
        self._items[user["id"]] = user
        self._next_id += 1
        return user

    def update(self, user_id: int, data: dict) -> dict:
        user = self._items[user_id]
        user.update(data)  # el id no viene en data, por lo que se conserva
        return user

    def delete(self, user_id: int) -> None:
        self._items.pop(user_id, None)


class DeviceSystemRepository:
    def __init__(self) -> None:
        self._items: dict[int, dict] = {}
        self._next_id = 1

    def list(
        self,
        *,
        device_status: DeviceStatus | None,
        owner_id: int | None,
        system_type: str | None,
        skip: int,
        limit: int,
    ) -> list[dict]:
        items = list(self._items.values())
        if device_status is not None:
            items = [d for d in items if d["status"] == device_status]
        if owner_id is not None:
            items = [d for d in items if d["owner_id"] == owner_id]
        if system_type is not None:
            items = [d for d in items if d["system_type"] == system_type]
        return items[skip : skip + limit]

    def get(self, device_id: int) -> dict | None:
        return self._items.get(device_id)

    def get_by_serial(self, serial_number: str) -> dict | None:
        return next(
            (d for d in self._items.values() if d["serial_number"].lower() == serial_number.lower()),
            None,
        )

    def create(self, data: dict) -> dict:
        now = _now()
        device = {"id": self._next_id, **data, "created_at": now, "updated_at": now}
        self._items[device["id"]] = device
        self._next_id += 1
        return device

    def update(self, device_id: int, changes: dict) -> dict:
        device = self._items[device_id]
        device.update(changes)
        device["updated_at"] = _now()
        return device

    def delete(self, device_id: int) -> None:
        self._items.pop(device_id, None)


# =============================================================================
# 4. SERVICE (reglas de negocio y manejo de errores)
# =============================================================================


class DeviceSystemService:
    # Campos que sí pueden ponerse en null mediante PATCH
    NULLABLE_FIELDS = {"owner_id", "description"}

    def __init__(self, devices: DeviceSystemRepository, users: UserRepository) -> None:
        self.devices = devices
        self.users = users

    # -- validaciones reutilizables --
    def _ensure_owner_exists(self, owner_id: int | None) -> None:
        if owner_id is not None and self.users.get(owner_id) is None:
            raise NotFoundError(f"No existe el usuario propietario con id {owner_id}")

    def _ensure_serial_is_free(self, serial_number: str, exclude_id: int | None = None) -> None:
        other = self.devices.get_by_serial(serial_number)
        if other is not None and other["id"] != exclude_id:
            raise ConflictError(
                f"Ya existe un device_system registrado con el número de serie {serial_number}"
            )

    # -- casos de uso (CRUD) --
    def list(self, **filters) -> list[dict]:
        return self.devices.list(**filters)

    def get(self, device_id: int) -> dict:
        device = self.devices.get(device_id)
        if device is None:
            raise NotFoundError(f"No existe el device_system con id {device_id}")
        return device

    def create(self, data: DeviceSystemCreate) -> dict:
        self._ensure_owner_exists(data.owner_id)
        self._ensure_serial_is_free(data.serial_number)
        return self.devices.create(data.model_dump())

    def replace(self, device_id: int, data: DeviceSystemCreate) -> dict:
        self.get(device_id)  # lanza 404 si no existe
        self._ensure_owner_exists(data.owner_id)
        self._ensure_serial_is_free(data.serial_number, exclude_id=device_id)
        return self.devices.update(device_id, data.model_dump())

    def patch(self, device_id: int, data: DeviceSystemUpdate) -> dict:
        self.get(device_id)  # lanza 404 si no existe
        changes = {
            key: value
            for key, value in data.model_dump(exclude_unset=True).items()
            if value is not None or key in self.NULLABLE_FIELDS
        }
        if changes.get("owner_id") is not None:
            self._ensure_owner_exists(changes["owner_id"])
        if "serial_number" in changes:
            self._ensure_serial_is_free(changes["serial_number"], exclude_id=device_id)
        return self.devices.update(device_id, changes)

    def delete(self, device_id: int) -> None:
        self.get(device_id)  # lanza 404 si no existe
        self.devices.delete(device_id)


# =============================================================================
# 5. DEPENDENCY INJECTION
#    Los routers no crean objetos: los "piden" con Depends y FastAPI los inyecta.
#    En pruebas se pueden sustituir con app.dependency_overrides[get_device_repo].
# =============================================================================

_user_repo = UserRepository()
_device_repo = DeviceSystemRepository()

# Datos de ejemplo (el correo de Sofía provoca el 400 al intentar registrarla otra vez)
_user_repo.create(
    {"name": "Sofía Restrepo", "email": "sofía@correo.com", "role": "user", "is_active": True}
)
_user_repo.create(
    {"name": "Luis Ramírez", "email": "luis@correo.com", "role": "user", "is_active": True}
)
_device_repo.create(
    {
        "name": "Gateway Principal",
        "serial_number": "GW-0001",
        "system_type": "linux",
        "version": "1.0.0",
        "status": DeviceStatus.ACTIVE,
        "owner_id": 1,
        "description": "Dispositivo de ejemplo",
    }
)


def get_user_repo() -> UserRepository:
    return _user_repo


def get_device_repo() -> DeviceSystemRepository:
    return _device_repo


UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]


def get_device_service(
    devices: Annotated[DeviceSystemRepository, Depends(get_device_repo)],
    users: UserRepoDep,
) -> DeviceSystemService:
    return DeviceSystemService(devices, users)


DeviceServiceDep = Annotated[DeviceSystemService, Depends(get_device_service)]


@dataclass
class Pagination:
    skip: int
    limit: int


def get_pagination(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros a devolver"),
) -> Pagination:
    return Pagination(skip=skip, limit=limit)


PaginationDep = Annotated[Pagination, Depends(get_pagination)]
DeviceId = Annotated[int, Path(ge=1, description="ID del device_system")]
UserId = Annotated[int, Path(ge=1, description="ID del usuario")]

# =============================================================================
# 6. ROUTERS
# =============================================================================

users_router = APIRouter(prefix="/users", tags=["Users"])
devices_router = APIRouter(prefix="/device_systems", tags=["Device Systems"])

# ---- Users ------------------------------------------------------------------


@users_router.get("", response_model=list[UserOut], summary="Listar usuarios")
def list_users(repo: UserRepoDep):
    return repo.list_all()


@users_router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Obtener un usuario por ID",
    responses=R_404,
)
def get_user(user_id: UserId, repo: UserRepoDep):
    user = repo.get(user_id)
    if user is None:
        raise NotFoundError(f"No existe el usuario con id {user_id}")
    return user


@users_router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un usuario",
    responses={400: {"model": ErrorResponse, "description": "El correo ya está registrado"}},
)
def create_user(user: UserCreate, repo: UserRepoDep):
    if repo.get_by_email(user.email):
        raise BadRequestError(f"Ya existe un usuario registrado con el correo {user.email}")
    return repo.create(user.model_dump())


@users_router.put(
    "/{user_id}",
    response_model=UserOut,
    summary="Reemplazar un usuario (actualización completa)",
    description="Todos los campos son obligatorios: los datos enviados reemplazan por "
    "completo los del usuario. Devuelve el usuario ya actualizado.",
    responses={
        **R_404,
        400: {"model": ErrorResponse, "description": "El correo pertenece a otro usuario"},
    },
)
def replace_user(user_id: UserId, data: UserReplace, repo: UserRepoDep):
    if repo.get(user_id) is None:
        raise NotFoundError(f"No existe el usuario con id {user_id}")
    other = repo.get_by_email(data.email)
    if other is not None and other["id"] != user_id:
        raise BadRequestError(f"Ya existe un usuario registrado con el correo {data.email}")
    return repo.update(user_id, data.model_dump())


@users_router.patch(
    "/{user_id}",
    response_model=UserOut,
    summary="Actualizar parcialmente un usuario",
    description="Envía solo los campos que quieras cambiar; el resto de los datos del "
    "usuario queda igual. Devuelve el usuario ya actualizado.",
    responses={
        **R_404,
        400: {
            "model": ErrorResponse,
            "description": "Body vacío o correo perteneciente a otro usuario",
        },
    },
)
def patch_user(user_id: UserId, data: UserUpdate, repo: UserRepoDep):
    if repo.get(user_id) is None:
        raise NotFoundError(f"No existe el usuario con id {user_id}")

    # Solo los campos enviados (y no nulos) se modifican
    changes = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    if not changes:
        raise BadRequestError("Debes enviar al menos un campo para actualizar")

    if "email" in changes:
        other = repo.get_by_email(changes["email"])
        if other is not None and other["id"] != user_id:
            raise BadRequestError(f"Ya existe un usuario registrado con el correo {changes['email']}")

    return repo.update(user_id, changes)


@users_router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Eliminar un usuario",
    description="Elimina el usuario y responde `200` con un mensaje de confirmación.",
    responses=R_404,
)
def delete_user(user_id: UserId, repo: UserRepoDep):
    if repo.get(user_id) is None:
        raise NotFoundError(f"No existe el usuario con id {user_id}")
    repo.delete(user_id)
    return {"detail": f"Usuario con id {user_id} eliminado correctamente"}


# ---- Device systems (CRUD completo) -----------------------------------------


@devices_router.post(
    "",
    response_model=DeviceSystemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un device_system",
    description="Registra un nuevo dispositivo. El número de serie debe ser único y, "
    "si se envía `owner_id`, el usuario debe existir.",
    responses={**R_404, **R_409},
)
def create_device_system(data: DeviceSystemCreate, service: DeviceServiceDep):
    return service.create(data)


@devices_router.get(
    "",
    response_model=list[DeviceSystemOut],
    summary="Listar device_systems",
    description="Devuelve los dispositivos con filtros opcionales y paginación.",
)
def list_device_systems(
    service: DeviceServiceDep,
    pagination: PaginationDep,
    device_status: Annotated[
        DeviceStatus | None, Query(alias="status", description="Filtrar por estado")
    ] = None,
    owner_id: Annotated[int | None, Query(ge=1, description="Filtrar por propietario")] = None,
    system_type: Annotated[SystemType | None, Query(description="Filtrar por tipo")] = None,
):
    return service.list(
        device_status=device_status,
        owner_id=owner_id,
        system_type=system_type,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@devices_router.get(
    "/{device_id}",
    response_model=DeviceSystemOut,
    summary="Obtener un device_system por ID",
    responses=R_404,
)
def get_device_system(device_id: DeviceId, service: DeviceServiceDep):
    return service.get(device_id)


@devices_router.put(
    "/{device_id}",
    response_model=DeviceSystemOut,
    summary="Reemplazar un device_system (actualización completa)",
    responses={**R_404, **R_409},
)
def replace_device_system(device_id: DeviceId, data: DeviceSystemCreate, service: DeviceServiceDep):
    return service.replace(device_id, data)


@devices_router.patch(
    "/{device_id}",
    response_model=DeviceSystemOut,
    summary="Actualizar parcialmente un device_system",
    description="Solo se modifican los campos enviados en el body.",
    responses={**R_404, **R_409},
)
def patch_device_system(device_id: DeviceId, data: DeviceSystemUpdate, service: DeviceServiceDep):
    return service.patch(device_id, data)


@devices_router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un device_system",
    responses=R_404,
)
def delete_device_system(device_id: DeviceId, service: DeviceServiceDep):
    service.delete(device_id)


# =============================================================================
# 7. APLICACIÓN + SWAGGER/OPENAPI + HANDLERS DE ERRORES
# =============================================================================

tags_metadata = [
    {"name": "Users", "description": "Gestión de usuarios."},
    {"name": "Device Systems", "description": "CRUD completo de dispositivos/sistemas."},
]

app = FastAPI(
    title="API de Usuarios y Device Systems",
    description=(
        "API REST con CRUD completo, manejo de errores centralizado e inyección de "
        "dependencias.\n\n"
        "**Códigos de error habituales:** `400` datos de negocio inválidos, "
        "`404` recurso inexistente, `409` conflicto (duplicado), "
        "`422` el body no cumple el esquema, `500` error interno."
    ),
    version="2.0.0",
    openapi_tags=tags_metadata,
)

app.include_router(users_router)
app.include_router(devices_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Último recurso: nunca se filtran detalles internos al cliente
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})