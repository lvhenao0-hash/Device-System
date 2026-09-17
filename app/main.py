<<<<<<< HEAD
# app/main.py
from fastapi import FastAPI, Request
=======
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

>>>>>>> a0aa56d0e8304b04ff5cea7ad42de91ffb0e6069
from app.routes import user_routes

tags_metadata = [
    {
        "name": "Usuarios",
        "description": "Operaciones CRUD sobre el recurso de usuarios del sistema device_systems.",
    },
]

app = FastAPI(
<<<<<<< HEAD
    title="device_systems API",
    description="API REST para la gestion de usuarios del sistema device_systems",
    version="2.0.0",
    contact={"name": "Juan Camilo Sarrazola", "email": "camilo@correo.com"},
    openapi_tags=[{"name": "Users", "description": "Operaciones CRUD sobre usuarios"}],
=======
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
>>>>>>> a0aa56d0e8304b04ff5cea7ad42de91ffb0e6069
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


@app.get("/", tags=["Raiz"])
def raiz():
    return {"mensaje": "Bienvenido a device_systems API v2.0. Visita /docs para ver la documentacion."}