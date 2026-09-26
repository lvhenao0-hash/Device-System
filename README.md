device_systems – EV11 Seguridad y Autenticación

API REST desarrollada con FastAPI para la gestión de usuarios, dispositivos y préstamos.
Esta versión corresponde a la evolución GA1-220501096-01-AA1-EV11, cuyo objetivo es incorporar seguridad, autenticación, autorización y protección de la API.

Estado del proyecto recibido: la carpeta entregada corresponde a la versión anterior con FastAPI + SQLAlchemy + Alembic, recursos users, devices y loans, relaciones, joins y filtros. EV11 debe agregarse sobre esta base.

1. Objetivo de EV11

La aplicación debe incorporar:

Validaciones avanzadas con Pydantic v2.

Hash seguro de contraseñas con Passlib.

OAuth2 + JWT.

Protección de rutas mediante dependencias.

Autorización básica por roles.

CORS.

Middleware personalizado.

Rate limiting con SlowAPI.

Documentación Swagger/OpenAPI.

Migración Alembic para los nuevos campos de autenticación.

La guía de la actividad establece los endpoints /auth/register, /auth/login y /auth/me, además de la protección de las rutas existentes. fileciteturn0file0L215-L250

2. Estructura objetivo

device_systems/
├── app/
│   ├── main.py
│   ├── auth/
│   │   ├── auth_routes.py
│   │   ├── auth_service.py
│   │   └── security.py
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   ├── loan_schema.py
│   │   └── auth_schema.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   ├── dependencies/
│   │   ├── database_dependency.py
│   │   └── auth_dependency.py
│   └── middlewares/
│       └── request_middleware.py
├── alembic/
│   └── versions/
├── .env
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md

Esta estructura sigue la estructura sugerida oficialmente para EV11. fileciteturn0file0L92-L144

3. Dependencias

Instalar:

pip install python-jose[cryptography] passlib[bcrypt] slowapi python-multipart

Mantener las dependencias existentes de FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, email-validator y python-dotenv. fileciteturn0file0L145-L157

Ejemplo de requirements.txt:

fastapi
uvicorn
sqlalchemy
alembic
pydantic
email-validator
python-dotenv
python-jose[cryptography]
passlib[bcrypt]
slowapi
python-multipart

4. Variables de entorno

Crear .env:

SECRET_KEY=cambiar_por_una_clave_secreta_larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Crear .env.example sin secretos reales:

SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

No subir .env al repositorio.

5. Actualizar User

Agregar al modelo User:

hashed_password = Column(String, nullable=False)
role = Column(String, nullable=False)
is_active = Column(Boolean, default=True)

La contraseña debe almacenarse solamente como hash y hashed_password nunca debe exponerse en los modelos de respuesta. fileciteturn0file0L161-L194

Después:

alembic revision --autogenerate -m "add authentication fields to users"
alembic upgrade head

6. Seguridad de contraseñas y JWT

Crear app/auth/security.py con funciones equivalentes a:

get_password_hash(password)
verify_password(plain_password, hashed_password)
create_access_token(data: dict)
decode_access_token(token: str)

La guía exige hash de contraseñas y creación/validación de tokens JWT. fileciteturn0file0L177-L194

7. Schemas Pydantic v2

Crear app/schemas/auth_schema.py.

Debe contemplar:

UserRegister

UserLogin

Token

TokenData

La contraseña debe cumplir:

mínimo 8 caracteres;

una mayúscula;

una minúscula;

un número;

sin espacios.

Usar Field(), field_validator, model_validator cuando corresponda y ConfigDict(from_attributes=True) en respuestas. fileciteturn0file0L196-L214

8. Endpoints de autenticación

Crear app/auth/auth_routes.py.

Registro

POST /auth/register

Debe validar nombre, email, unicidad, contraseña y rol, y guardar el hash, no la contraseña original.

Login

POST /auth/login

Respuesta:

{
  "access_token": "token_generado",
  "token_type": "bearer"
}

Usuario autenticado

GET /auth/me
Authorization: Bearer <token>

No debe devolver hashed_password. fileciteturn0file0L225-L250

9. Protección por roles

Crear app/dependencies/auth_dependency.py.

Dependencias mínimas:

get_current_user
get_current_active_user
require_admin

Protecciones exigidas:

Endpoint

Protección

GET /users

Usuario autenticado

GET /users/{user_id}

Usuario autenticado

POST /devices

admin o support

PUT /devices/{device_id}

admin o support

DELETE /devices/{device_id}

admin

POST /loans

Usuario autenticado

PATCH /loans/{loan_id}/return

admin o support

GET /loans/details

admin o support

La guía establece 401 Unauthorized para token inexistente/inválido y 403 Forbidden para falta de permisos. fileciteturn0file0L251-L275

10. CORS

En app/main.py configurar CORSMiddleware.

Para desarrollo:

allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]

En producción conviene declarar orígenes concretos en lugar de usar "*" cuando se trabajan credenciales. La actividad pide explicar esta decisión en el README. fileciteturn0file0L277-L292

11. Middleware

Crear app/middlewares/request_middleware.py.

Debe:

medir el tiempo de respuesta;

agregar X-Process-Time;

agregar X-App-Name: device_systems;

generar o propagar X-Request-ID;

registrar método, ruta y estado HTTP.

Ejemplo de resultado:

X-App-Name: device_systems
X-Process-Time: 0.0042
X-Request-ID: 8f42e9c1

Estos requisitos corresponden a la Fase 10. fileciteturn0file0L294-L304

12. Rate limiting

Configurar SlowAPI.

Límites mínimos:

Endpoint

Límite

POST /auth/login

5/minuto

POST /auth/register

3/minuto

GET /users

30/minuto

POST /loans

10/minuto

Al superar el límite debe aparecer 429 Too Many Requests. La evidencia debe mostrar al menos una prueba donde se active el límite. fileciteturn0file0L306-L316

13. Swagger/OpenAPI

Configurar:

app = FastAPI(
    title="device_systems API",
    description="API REST segura para gestión de usuarios, dispositivos y préstamos",
    version="3.0.0"
)

Tags:

Auth

Users

Devices

Loans

Security

Swagger debe mostrar endpoints protegidos, OAuth2, modelos, respuestas y errores. fileciteturn0file0L317-L340

14. Ejecución

Desde la raíz:

uvicorn app.main:app --reload

Abrir:

http://127.0.0.1:8000/docs

15. Pruebas obligatorias

Realizar y capturar:

Registro correcto.

Registro con contraseña débil.

Registro con email duplicado.

Login correcto.

Login con contraseña incorrecta.

/auth/me.

Ruta protegida sin token.

Token inválido.

Usuario sin permisos.

Crear dispositivo con rol permitido.

Eliminar dispositivo con rol no permitido.

CORS.

Cabeceras del middleware.

Rate limiting.

Swagger/OpenAPI.

La lista corresponde a la Fase 13 de la actividad. fileciteturn0file0L341-L356

16. Evidencias para README

La guía solicita evidencias de:

estructura del proyecto;

migración Alembic;

registro;

login y token;

/auth/me;

acceso sin token;

acceso con rol no permitido;

Swagger con OAuth2;

cabeceras del middleware;

rate limiting;

CORS;

reflexión final. fileciteturn0file0L413-L425

17. Git

Crear la rama solicitada:

git checkout -b device_systems_security

Después de probar:

git add .
git commit -m "feat: add API security authentication middleware cors and rate limiting"
git push -u origin device_systems_security

La evidencia de aprendizaje solicita una rama llamada device_systems_security que posteriormente debe unificarse con main. fileciteturn0file0L394-L412

18. Checklist final

User tiene hashed_password.

Contraseñas nunca se guardan en texto plano.

Registro funciona.

Login genera JWT.

/auth/me funciona con Bearer token.

Rutas protegidas.

Roles admin, support, user.

Respuestas 401/403 correctas.

Pydantic v2 con validaciones.

CORS configurado.

Middleware funcionando.

X-App-Name, X-Process-Time, X-Request-ID.

Rate limiting devuelve 429.

Swagger muestra OAuth2.

Alembic aplicado.

.env.example incluido.

README actualizado.

Evidencias capturadas.

Video máximo 15 minutos.

19. Reflexión final

La evolución a EV11 agrega una capa de seguridad sobre la API existente. El proyecto pasa de una API con persistencia, relaciones y CRUD a una API que controla identidad, acceso, validación, trazabilidad y abuso de peticiones. La seguridad se implementa como parte de la arquitectura y no como una funcionalidad aislada.