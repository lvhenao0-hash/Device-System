from fastapi import FastAPI, Request
from app.routes import user_routes, device_routes, loan_routes

tags_metadata = [
    {"name": "Users", "description": "Operaciones CRUD sobre usuarios."},
    {"name": "Devices", "description": "CRUD y filtros de dispositivos."},
    {"name": "Loans", "description": "Gestión de préstamos, devoluciones y consultas relacionadas."},
    {"name": "Raiz", "description": "Endpoint de bienvenida."},
]

app = FastAPI(
    title="device_systems API",
    description="API REST para gestionar usuarios, dispositivos y préstamos con FastAPI, SQLAlchemy y Alembic.",
    version="4.0.0",
    openapi_tags=tags_metadata,
)

@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "4.0.0"
    return response

app.include_router(user_routes.router)
app.include_router(device_routes.router)
app.include_router(loan_routes.router)

@app.get("/", tags=["Raiz"], summary="Bienvenida")
def raiz():
    return {"mensaje": "Bienvenido a device_systems API v4.0. Visita /docs para consultar Swagger."}
