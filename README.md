# device_systems

API REST desarrollada con **FastAPI** para la gestión de usuarios, dispositivos y préstamos, con persistencia en base de datos mediante **SQLAlchemy**, migraciones controladas con **Alembic**, relaciones entre modelos y consultas avanzadas con **joins** y filtros.

Proyecto desarrollado por: **Laura Vanessa Henao**

---

## Evolución del proyecto

- **EV09**: migración de almacenamiento en memoria a persistencia con SQLAlchemy + SQLite, CRUD completo de `users`.
- **EV10** *(actual)*: incorporación de Alembic, nuevos recursos `devices` y `loans`, relaciones entre modelos, consultas con joins y filtros avanzados.

---

## Estructura del proyecto

device_systems/
│── app/
│ │── main.py
│ │
│ │── database/
│ │ │── connection.py
│ │
│ │── models/
│ │ │── user_model.py
│ │ │── device_model.py
│ │ │── loan_model.py
│ │
│ │── schemas/
│ │ │── user_schema.py
│ │ │── device_schema.py
│ │ │── loan_schema.py
│ │
│ │── routes/
│ │ │── user_routes.py
│ │ │── device_routes.py
│ │ │── loan_routes.py
│ │ │── user_loan_routes.py
│ │
│ │── services/
│ │ │── user_service.py
│ │ │── device_service.py
│ │ │── loan_service.py
│ │
│ │── dependencies/
│ │── database_dependency.py
│ │── user_dependencies.py
│
│── alembic/
│ │── versions/
│
│── alembic.ini
│── requirements.txt
│── README.md


---

## Modelos y relaciones

| Modelo | Descripción |
|---|---|
| `User` | Usuarios del sistema (`name`, `email`, `role`, `is_active`, `created_at`) |
| `Device` | Dispositivos disponibles para préstamo (`name`, `serial_number`, `device_type`, `brand`, `is_available`, `created_at`) |
| `Loan` | Registro de préstamo de un dispositivo a un usuario (`user_id`, `device_id`, `loan_date`, `return_date`, `status`) |

**Relaciones (`relationship()` + `back_populates`):**
- Un usuario puede tener muchos préstamos (`User.loans` ↔ `Loan.user`)
- Un dispositivo puede aparecer en muchos préstamos históricos (`Device.loans` ↔ `Loan.device`)
- Cada préstamo pertenece a un usuario y a un dispositivo (`ForeignKey` + integridad referencial)

---

## Migraciones con Alembic

Instalación e inicialización:

```bash
pip install alembic
alembic init alembic
```

![Ejecución de alembic init](images/evo10/alembic_init.png)

Generación de la migración (autogenerada a partir de los modelos `Device` y `Loan`):

```bash
alembic revision --autogenerate -m "create devices and loans tables"
```

![Creación de migración con autogenerate](images/evo10/alembic_revision_autogenerate.png)

Aplicación de la migración:

```bash
alembic upgrade head
```

![Aplicación de migración](images/evo10/alembic_init.png)

Historial de migraciones aplicadas:

```bash
alembic history
alembic current
```

![Historial de migraciones](images/evo10/alembic_history.png)

Estructura de tablas generadas en la base de datos:

![Estructura de tablas](images/evo10/estructura_tablas.png)

---

## Documentación Swagger / OpenAPI

Disponible en `/docs` (Swagger UI) y `/redoc`, organizada por tags: **Users**, **Devices**, **Loans**.

![Swagger UI - vista general](images/evo10/swagger_general.png)

---

## Fase 13 – Pruebas funcionales mínimas (GFPI-F-135 V04)

Escenarios probados de extremo a extremo con Postman, sobre una base de datos migrada desde cero con Alembic.

| # | Escenario | Método y endpoint | Evidencia |
|---|---|---|---|
| 1 | Ejecutar migraciones con Alembic | Terminal: `alembic upgrade head` | ![Migraciones Alembic](images/evo10/alembic_upgrade_head.png) 

| 2 | Crear usuario | `POST /users` | ![Crear usuario](images/evo10/post_usuario_creado.png) 

| 3 | Crear dispositivo | `POST /devices` | ![Crear dispositivo](images/evo10/post_dispositivo_creado.png) 

| 4 | Crear préstamo | `POST /loans` | ![Crear préstamo](images/evo10/post_prestamo_creado.png) 

| 5 | Intentar prestar un dispositivo no disponible | `POST /loans` → 409 Conflict | ![Dispositivo no disponible](images/evo10/prestamo_conflicto_409.png) 

| 6 | Listar préstamos con información de usuario y dispositivo | `GET /loans/details` | ![Préstamos con detalle](images/evo10/get_prestamos_detalle.png) 

| 7 | Filtrar préstamos por estado | `GET /loans/details?status=active` | ![Filtro por estado](images/evo10/get_prestamos_filtro_estado.png) 

| 8 | Filtrar préstamos por tipo de dispositivo | `GET /loans/details?device_type=laptop` | ![Filtro por tipo](images/evo10/get_prestamos_filtro_tipo.png) 

| 9 | Consultar préstamos de un usuario | `GET /users/{user_id}/loans` | ![Préstamos de un usuario](images/evo10/get_prestamos_usuario.png) 

| 10 | Devolver un dispositivo | `PATCH /loans/{loan_id}/return` | ![Devolver dispositivo](images/evo10/patch_prestamo_devolucion.png) 

| 11 | Validar que el dispositivo vuelva a estar disponible | `GET /devices/{device_id}` (`is_available: true`) | ![Dispositivo disponible](images/evo10/get_dispositivo_disponible.png) 

| 12 | Consultar historial de préstamos del dispositivo | `GET /devices/{device_id}/loans` | ![Historial del dispositivo](images/evo10/get_historial_dispositivo.png) |

---

## Evidencias funcionales

### Gestión de usuarios

| Acción | Evidencia |
|---|---|
| Listar usuarios | ![Listar usuarios](images/evo10/postman_get_users.png) 

| Crear usuario | ![Crear usuario](images/evo10/postman_post_user_exitoso.png) 

### Gestión de dispositivos

| Acción | Evidencia |
|---|---|
| Crear dispositivo | ![Crear dispositivo](images/evo10/postman_post_device_exitoso.png) 

| Serial duplicado (error) | ![Serial duplicado](images/evo10/postman_post_device_serial_duplicado_400.png) 

| Consultar dispositivo puntual | ![Consultar dispositivo](images/evo10/postman_get_device_puntual.png) 

| Dispositivo inexistente (error) | ![Dispositivo inexistente](images/evo10/postman_get_device_404.png) 

### Gestión de préstamos

| Acción | Evidencia |
|---|---|
| Crear préstamo | ![Crear prestamo](images/evo10/postman_post_loan_exitoso.png) 

| Dispositivo no disponible (error) | ![Dispositivo no disponible](images/evo10/postman_post_loan_409_no_disponible.png) 

| Devolver dispositivo | ![Devolver dispositivo](images/evo10/postman_patch_loan_return_exitoso.png) 

| Préstamo ya devuelto (error) | ![Prestamo ya devuelto](images/evo10/postman_patch_loan_return_409.png) 

### Consultas con joins

| Acción | Evidencia 
|---|---|
| Préstamos con información relacionada (`/loans/details`) | ![Loans details](images/evo10/postman_get_loans_details.png) 

| Préstamos de un usuario (`/users/{id}/loans`) | ![Loans de un usuario](images/evo10/postman_get_user_loans.png) 

| Historial de préstamos de un dispositivo (`/devices/{id}/loans`) | ![Historial de dispositivo](images/evo10/postman_get_device_loans.png) 

### Filtros aplicados

| Filtro | Evidencia |
|---|---|
| Préstamos por estado (`?status=active`) | ![Filtro por estado](images/evo10/postman_get_loans_filter_status.png) 

| Préstamos por tipo de dispositivo (`?device_type=laptop`) | ![Filtro por tipo](images/evo10/postman_get_loans_filter_device_type.png) 

---

## Manejo de errores

| Caso | Código |
|---|---|
| Registro creado | 201 Created |
| Consulta exitosa | 200 OK |
| Devolución exitosa | 200 OK |
| Eliminación exitosa | 204 No Content |
| Recurso no encontrado | 404 Not Found |
| Dato duplicado (serial repetido) | 400 Bad Request |
| Regla de negocio incumplida (dispositivo no disponible / préstamo ya devuelto) | 409 Conflict |
| Error de validación | 422 Unprocessable Entity |

---

## Flujo de Git

Todo el desarrollo se hizo sobre ramas `feature/*`, mergeadas a `develop` con `--no-ff`. Al cierre de la actividad, se creó la rama `device_systems_alembic_relaciones` desde la punta de `develop`, y se mergeó a `main` con `--no-ff`, tal como lo exige la guía.

---

## Reflexión

Esta actividad me enseñó a tratar la base de datos como parte del código, no como algo fijo: cada cambio pasa por una migración con Alembic, que permite evolucionar el esquema sin perder los datos existentes. Modelar las relaciones entre User, Device y Loan me hizo pensar en reglas de negocio reales (validar disponibilidad, actualizar estados en cascada) en lugar de CRUDs aislados. Las consultas con joins y el manejo diferenciado de errores (400 vs 409) terminaron de darle a la API un comportamiento mucho más cercano a un sistema real que a un ejercicio académico.