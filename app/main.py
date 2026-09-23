from fastapi import FastAPI, Request
from app.database.connection import Base, engine
from app.routes import user_routes

Base.metadata.create_all(bind=engine)

tags_metadata = [
    {"name": "Users", "description": "Operaciones CRUD sobre usuarios, persistidas en base de datos."},
    {"name": "Raiz", "description": "Endpoint de bienvenida."},
]

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestion de usuarios del sistema device_systems, con persistencia en base de datos.",
    version="3.0.0",
    contact={"name": "Juan Camilo Sarrazola", "email": "camilo@correo.com"},
    openapi_tags=tags_metadata,
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0.0"
    return response


app.include_router(user_routes.router)


@app.get("/", tags=["Raiz"])
def raiz():
    return {"mensaje": "Bienvenido a device_systems API v3.0 (con base de datos). Visita /docs para ver la documentacion."}