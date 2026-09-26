# device_systems — GA1-220501096-01-AA1-EV10

**Actividad:** FastAPI Avanzado: Migraciones con Alembic, Asociaciones de Modelos y Consultas con Joins.

## Objetivo

Esta versión evoluciona el proyecto anterior para gestionar **usuarios, dispositivos y préstamos**, incorporando SQLAlchemy, relaciones `One-to-Many / Many-to-One`, migraciones con Alembic, consultas con `join()` y filtros avanzados.

## Tecnologías

- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic v2
- SQLite
- Uvicorn
- Postman / Thunder Client

## Estructura principal

```text
device_systems/
├── app/
│   ├── main.py
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   └── services/
│       ├── user_service.py
│       ├── device_service.py
│       └── loan_service.py
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 0001_devices_and_loans.py
├── alembic.ini
├── requirements.txt
└── README.md
```

## Instalación

Desde la raíz del proyecto:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Migraciones Alembic

Inicialmente se dejó configurado Alembic y una migración para `devices` y `loans`.

```bash
alembic history
alembic upgrade head
```

Para generar una nueva migración después de modificar los modelos:

```bash
alembic revision --autogenerate -m "descripcion del cambio"
alembic upgrade head
```

Para volver una migración:

```bash
alembic downgrade -1
```

## Ejecutar la API

```bash
uvicorn app.main:app --reload
```

Documentación:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Relaciones

### User → Loan

Un usuario puede tener muchos préstamos:

```python
loans = relationship("Loan", back_populates="user")
```

### Device → Loan

Un dispositivo puede aparecer en varios préstamos históricos:

```python
loans = relationship("Loan", back_populates="device")
```

### Loan → User / Device

Cada préstamo pertenece a un usuario y a un dispositivo:

```python
user = relationship("User", back_populates="loans")
device = relationship("Device", back_populates="loans")
```

## Endpoints

### Users

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/users` | Listar usuarios |
| GET | `/users/{user_id}` | Consultar usuario |
| POST | `/users` | Crear usuario |
| PUT | `/users/{user_id}` | Actualizar usuario |
| PATCH | `/users/{user_id}` | Actualización parcial |
| DELETE | `/users/{user_id}` | Eliminar usuario |
| GET | `/users/{user_id}/loans` | Préstamos del usuario |

### Devices

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/devices` | Listar dispositivos |
| GET | `/devices/{device_id}` | Consultar dispositivo |
| POST | `/devices` | Crear dispositivo |
| PUT | `/devices/{device_id}` | Actualizar dispositivo |
| PATCH | `/devices/{device_id}` | Actualización parcial |
| DELETE | `/devices/{device_id}` | Eliminar dispositivo |
| GET | `/devices/{device_id}/loans` | Historial del dispositivo |

Filtros:

```text
GET /devices?device_type=laptop
GET /devices?is_available=true
GET /devices?brand=Lenovo
GET /devices?search=ThinkPad
```

### Loans

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/loans` | Listar préstamos |
| GET | `/loans/{loan_id}` | Consultar préstamo |
| POST | `/loans` | Crear préstamo |
| PATCH | `/loans/{loan_id}/return` | Registrar devolución |
| GET | `/loans/details` | Consulta detallada con relaciones |

Filtros disponibles:

```text
GET /loans?status=active
GET /loans?user_email=aprendiz@sena.edu.co
GET /loans?device_type=laptop
GET /loans?user_id=1
GET /loans?device_id=1
```

## Regla de negocio del préstamo

Al crear un préstamo:

1. Se valida que exista el usuario.
2. Se valida que exista el dispositivo.
3. Se valida que el dispositivo esté disponible.
4. Se crea el préstamo con estado `active`.
5. El dispositivo pasa a `is_available = false`.

Al devolverlo:

1. Se valida que exista el préstamo.
2. Se evita devolver un préstamo que ya tenga estado `returned`.
3. Se establece `return_date`.
4. El estado cambia a `returned`.
5. El dispositivo vuelve a estar disponible.

## Consultas con JOIN

Las consultas de préstamos combinan `Loan`, `User` y `Device` mediante `join()` y aplican filtros con condiciones SQLAlchemy. También se utilizan `where/filter`, `ilike()` y condiciones combinadas mediante `and_()`.

El endpoint:

```text
GET /loans/details
```

devuelve una estructura similar a:

```json
{
  "loan_id": 1,
  "status": "active",
  "loan_date": "2026-09-24T10:00:00",
  "return_date": null,
  "user": {
    "id": 1,
    "name": "Ana Pérez",
    "email": "ana@sena.edu.co"
  },
  "device": {
    "id": 1,
    "name": "Laptop Lenovo ThinkPad",
    "serial_number": "LEN-2024-001",
    "device_type": "laptop"
  }
}
```

## Manejo de errores

- `201 Created`: creación correcta.
- `200 OK`: consultas, actualizaciones y devolución correcta.
- `204 No Content`: eliminación correcta.
- `400 Bad Request`: datos duplicados o solicitud inválida.
- `404 Not Found`: usuario, dispositivo o préstamo inexistente.
- `409 Conflict`: dispositivo no disponible o regla de negocio incumplida.
- `422 Unprocessable Entity`: validación de datos o filtro inválido.

## Pruebas funcionales sugeridas

1. `alembic upgrade head`.
2. Crear usuario.
3. Crear dispositivo.
4. Crear préstamo.
5. Intentar prestar nuevamente el mismo dispositivo y comprobar `409`.
6. Consultar `/loans/details`.
7. Filtrar por `status=active`.
8. Filtrar por `device_type=laptop`.
9. Consultar `/users/{id}/loans`.
10. Devolver el préstamo.
11. Verificar que el dispositivo vuelva a estar disponible.
12. Consultar `/devices/{id}/loans`.

## Evidencias para README / entrega

Agregar al documento final capturas de:

- `alembic init` (si se ejecutó durante la configuración).
- `alembic revision --autogenerate`.
- `alembic upgrade head`.
- `alembic history`.
- Estructura de tablas `users`, `devices` y `loans`.
- Swagger `/docs`.
- Creación de usuario.
- Creación de dispositivo.
- Creación de préstamo.
- Error al prestar dispositivo no disponible.
- `/loans/details`.
- Filtros.
- Devolución.
- Dispositivo nuevamente disponible.

## Rama solicitada

Para la evidencia de Git:

```bash
git checkout -b device_systems_alembic_relaciones
git add .
git commit -m "feat: implementar Alembic relaciones y prestamos"
git push -u origin device_systems_alembic_relaciones
```

Después de revisar la rama, realizar la integración con `main` según el flujo de trabajo solicitado.

## Reflexión

La evolución de `device_systems` permite pasar de un CRUD centrado en una sola tabla a un modelo relacional. Alembic permite controlar los cambios estructurales de la base de datos, mientras que `ForeignKey`, `relationship` y `back_populates` representan las asociaciones entre usuarios, dispositivos y préstamos. Las consultas con joins permiten obtener información relacionada sin separar la operación en múltiples consultas independientes.
