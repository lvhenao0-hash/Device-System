# device_systems

API REST desarrollada con **FastAPI** para la gestión de usuarios del sistema
`device_systems`. En su versión inicial permitía listar, filtrar, consultar
por ID y crear usuarios. Esta versión (**2.0.0**) evoluciona la API con
**CRUD completo** (`PUT`, `PATCH`, `DELETE`), manejo de errores con
`HTTPException`, códigos de estado HTTP correctos, documentación automática
Swagger/OpenAPI mejorada y reutilización de lógica mediante
**Dependency Injection** (`Depends()`).

## Tecnologías utilizadas

- Python 3
- FastAPI
- Uvicorn (servidor ASGI)
- Pydantic (validación de datos)

## Estructura del proyecto

A partir de esta versión, el proyecto separa responsabilidades en capas
(`routes`, `schemas`, `services`, `dependencies`, `data`):

```
device_systems/
├── app/
│   ├── main.py                        # Configuración de FastAPI, metadatos y manejo de errores 422
│   ├── routes/
│   │   └── user_routes.py             # Endpoints del recurso "users" (GET, POST, PUT, PATCH, DELETE)
│   ├── schemas/
│   │   └── user_schema.py             # Modelos Pydantic de entrada y salida
│   ├── services/
│   │   └── user_service.py            # Lógica de negocio (CRUD sobre los datos en memoria)
│   ├── dependencies/
│   │   └── user_dependencies.py       # Dependencias reutilizables con Depends()
│   └── data/
│       └── users_db.py                # Simulación de base de datos en memoria
├── Images/                            # Capturas de pantalla usadas en este README
├── requirements.txt                   # Dependencias del proyecto
└── README.md
```

## Instalación

1. Clona el repositorio y entra a la carpeta del proyecto:
   ```bash
   git clone <url-del-repositorio>
   cd device_systems
   ```

2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   ```

3. Actívalo:
   - En Windows (Git Bash):
     ```bash
     source venv/Scripts/activate
     ```
   - En Windows (PowerShell):
     ```powershell
     venv\Scripts\Activate.ps1
     ```
   - En macOS / Linux:
     ```bash
     source venv/bin/activate
     ```

4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Con el entorno virtual activado, levanta el servidor de desarrollo:

```bash
uvicorn app.main:app --reload
```

El servidor quedará disponible en:

- API: http://127.0.0.1:8000
- Documentación interactiva (Apidog): http://127.0.0.1:8000/users

## Endpoints disponibles

| Operación               | Método | Ruta            | Código esperado         |
|--------------------------|--------|-----------------|---------------------------|
| Endpoint de bienvenida    | GET    | `/`             | 200 OK                    |
| Listar usuarios (filtros opcionales `role`, `is_active`) | GET | `/users` | 200 OK |
| Consultar usuario         | GET    | `/users/{id}`   | 200 OK / 404 Not Found    |
| Crear usuario              | POST   | `/users`        | 201 Created / 400 / 422   |
| Actualizar completo        | PUT    | `/users/{id}`   | 200 OK / 404 / 400        |
| Actualizar parcial         | PATCH  | `/users/{id}`   | 200 OK / 404 / 400        |
| Eliminar usuario           | DELETE | `/users/{id}`   | 200 OK / 404 Not Found    |

### Endpoint GET /users

![GET /users](Images/get-users.png)

### Endpoint GET /users/{id}

![GET /users/{id}](Images/get-user-by-id.png)

### Endpoint POST /users

![POST /users](Images/post-users-error.png)
![POST /users](Images/post-users.png)

> Nota: agregar aquí capturas de Swagger UI (`/docs`) y ReDoc (`/redoc`) para los nuevos endpoints PUT, PATCH y DELETE.

## Ejemplos de peticiones y respuestas

### Actualización completa — `PUT /users/2`

Request:
```json
{
  "name": "Leo Carmona Actualizado",
  "email": "leo2@correo.com",
  "role": "support",
  "is_active": false
}
```

Response `200 OK`:
```json
{
  "id": 2,
  "name": "Leo Carmona Actualizado",
  "email": "leo2@correo.com",
  "role": "support",
  "is_active": false
}
```

### Actualización parcial — `PATCH /users/3`

Request:
```json
{
  "role": "admin"
}
```

Response `200 OK`:
```json
{
  "id": 3,
  "name": "Sebastian Lozano",
  "email": "sebastian@correo.com",
  "role": "admin",
  "is_active": false
}
```

### Errores controlados

Usuario no encontrado (`404`):
```json
{
  "detail": "No existe un usuario con id 999"
}
```

Correo duplicado (`400`):
```json
{
  "detail": "Ya existe un usuario registrado con el correo nueva@correo.com"
}
```

PATCH sin campos (`400`):
```json
{
  "detail": "Debe enviar al menos un campo para actualizar"
}
```

Datos inválidos, por ejemplo un rol fuera de `admin`/`support`/`user` (`422`):
```json
{
  "error": true,
  "message": "Datos inválidos",
  "detail": [ ... ]
}
```

## Uso de Depends() (Dependency Injection)

En `app/dependencies/user_dependencies.py` se definieron funciones reutilizables
que se inyectan en las rutas con `Depends()`, evitando duplicar lógica:

- **`obtener_usuario_o_404`**: busca un usuario por ID y lanza `404` si no existe. Se usa en GET por ID, PUT, PATCH y DELETE.
- **`validar_correo_no_duplicado_creacion`** / **`validar_correo_no_duplicado_actualizacion`** / **`validar_correo_patch_no_duplicado`**: validan que el correo no esté ya registrado por otro usuario, en POST, PUT y PATCH respectivamente.
- **`validar_patch_no_vacio`**: valida que el body de un PATCH no venga vacío.
- **`obtener_configuracion_api`**: dependencia de ejemplo que simula configuración general de la API.

Ejemplo:

```python
@router.get("/{user_id}", response_model=UserResponse)
def obtener_usuario(usuario: dict = Depends(obtener_usuario_o_404)):
    return usuario
```

## Manejo de errores implementado

La API usa `HTTPException` para responder de forma controlada ante:

- Usuario no encontrado (`404`).
- Correo electrónico duplicado, en creación y actualización (`400`).
- Intento de actualización parcial (PATCH) sin datos (`400`).
- Eliminación de usuario inexistente (`404`).

El rol del usuario se restringe con un tipo `Literal["admin", "support", "user"]`
en los schemas de Pydantic, por lo que un rol no permitido se rechaza
automáticamente con `422 Unprocessable Entity` junto con el resto de errores
de validación de datos.

Adicionalmente, se agregó un manejador personalizado de `RequestValidationError`
en `main.py` para que los errores `422` respondan con un formato estructurado:

```json
{
  "error": true,
  "message": "Datos inválidos",
  "detail": [ ... ]
}
```

## Reflexión sobre la evolución del proyecto

Respecto a la versión 1.0 (que solo contaba con `GET` y `POST`), esta versión
2.0.0 reorganiza el proyecto en capas (`routes`, `schemas`, `services`,
`dependencies`, `data`), agrega el CRUD completo (`PUT`, `PATCH`, `DELETE`),
estandariza el manejo de errores con `HTTPException`, aplica los códigos de
estado HTTP correctos para cada operación y reutiliza lógica común mediante
`Depends()`, manteniendo los datos y el estilo del proyecto original.

## Autor

Laura Vanessa Henao
# Device-System
