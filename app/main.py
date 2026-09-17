from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.routes import user_routes

tags_metadata = [
    {
        "name": "Usuarios",
        "description": "Operaciones CRUD sobre el recurso de usuarios del sistema device_systems.",
    },
]

app = FastAPI(
    title="device_systems",
    description=(
        "API REST para la gestión de usuarios del sistema **device_systems**. "
        "Permite crear, listar, consultar, filtrar, actualizar (completa y "
        "parcialmente) y eliminar usuarios, con manejo de errores, códigos "
        "de estado HTTP y documentación automática."
    ),
    version="2.0.0",
    contact={"name": "Laura Vanessa Henao"},
    openapi_tags=tags_metadata,
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0.0"
    return response


@app.exception_handler(RequestValidationError)
async def manejador_errores_validacion(request: Request, exc: RequestValidationError):
    """
    Personaliza la respuesta de errores de validación de Pydantic (422),
    devolviendo un formato consistente con el resto de errores de la API.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": True, "message": "Datos inválidos", "detail": exc.errors()},
    )


app.include_router(user_routes.router)


@app.get("/", tags=["Raíz"])
def raiz():
    """Endpoint de bienvenida, solo para confirmar que la API está viva."""
    return {"mensaje": "Bienvenido a device_systems API. Visita /docs para ver la documentación."}