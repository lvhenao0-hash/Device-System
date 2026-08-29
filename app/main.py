from fastapi import FastAPI, Request

from app.routes import user_routes

app = FastAPI(
    title="device_systems",
    description="API REST para la gestión de usuarios del sistema device_systems",
    version="1.0",
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"
    return response


app.include_router(user_routes.router)


@app.get("/", tags=["Raíz"])
def raiz():
    """Endpoint de bienvenida, solo para confirmar que la API está viva."""
    return {"mensaje": "Bienvenido a device_systems API. Visita /docs para ver la documentación."}