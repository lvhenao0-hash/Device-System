from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.auth.auth_routes import router as auth_router
from app.middlewares.rate_limiter import limiter
from app.middlewares.request_middleware import request_middleware
from app.routes import device_routes, loan_routes, user_loan_routes, user_routes

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST segura para la gestion de usuarios, dispositivos y prestamos "
        "del sistema device_systems. Evolucion EV11: autenticacion OAuth2 + JWT, "
        "autorizacion por roles, CORS, middleware personalizado y rate limiting."
    ),
    version="5.0.0",
    contact={"name": "Laura Vanessa Henao", "email": "Vanessa@correo.com"},
    openapi_tags=[
        {"name": "Auth", "description": "Registro, login y usuario autenticado"},
        {"name": "Users", "description": "Operaciones sobre usuarios y su historial de prestamos"},
        {"name": "Devices", "description": "Operaciones CRUD sobre dispositivos y su historial de prestamos"},
        {"name": "Loans", "description": "Gestion de prestamos de dispositivos"},
        {"name": "Security", "description": "Controles de seguridad de la API"},
    ],
)

# --- Rate limiting (SlowAPI) ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# --- CORS ---
# En desarrollo se listan explicitamente los origenes del frontend local.
# Con allow_credentials=True, CORS no permite usar allow_origins=["*"], por
# lo que en produccion tambien deben declararse los dominios reales en vez
# de un comodin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Middleware personalizado (tiempos, X-App-Name, X-Request-ID, logging) ---
app.middleware("http")(request_middleware)

# --- Routers ---
app.include_router(auth_router)
app.include_router(user_routes.router)
app.include_router(user_loan_routes.router)
app.include_router(device_routes.router)
app.include_router(loan_routes.router)


@app.get("/", tags=["Security"])
def raiz():
    return {"mensaje": "Bienvenido a device_systems API segura (EV11). Visita /docs."}
