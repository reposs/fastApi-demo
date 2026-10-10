# fastApi-demo ⚡

Demostración de API REST de alto rendimiento construida con **FastAPI**, **Pydantic V2** y **SQLModel**, siguiendo principios de **Clean Architecture**, inyección de dependencias estricta y seguridad robusta con **JWT** y **Argon2**.

- **Demo en vivo:** https://fastapi-demo-1373c10f.fastapicloud.dev/
- **Documentación Swagger UI:** https://fastapi-demo-1373c10f.fastapicloud.dev/docs
- **Documentación ReDoc:** https://fastapi-demo-1373c10f.fastapicloud.dev/redoc

---

## 🏗️ Arquitectura del Proyecto

El código está organizado siguiendo Clean Architecture y separación de responsabilidades:

```text
app/
├── api/
│   ├── dependencies.py      # Inyección de dependencias (CurrentUser, UserService, DB)
│   ├── routers/             # Routers modulares (auth, users, health)
│   └── v1/
│       └── api.py           # Agregador versionado (/api/v1)
├── core/
│   ├── config.py            # Configuración tipada con Pydantic Settings
│   ├── db/
│   │   └── database.py      # Engine SQLAlchemy, pool de conexiones y sesiones
│   ├── exceptions.py        # Excepciones de dominio desacopladas
│   ├── models/
│   │   └── user_model.py    # Modelo de persistencia SQLModel
│   ├── schemas/
│   │   ├── token_schema.py  # DTOs de autenticación y tokens JWT
│   │   └── user_schema.py   # DTOs de entrada y salida con validación
│   ├── security.py          # Hashing de contraseñas (Argon2) y tokens JWT
│   └── validators/
│       └── password_validator.py # Validador de complejidad de contraseñas
└── main.py                  # Instancia FastAPI, lifespan, CORS, middleware y handlers
tests/                       # Suite completa de pruebas unitarias
```

---

## 🚀 Comandos Rápidos

### Modo Desarrollo (con reload automático)
```bash
uv run fastapi dev
```

### Modo Producción
```bash
uv run fastapi run
```

### Ejecutar Pruebas Unitarias
```bash
uv run pytest
# O con el módulo estándar de Python:
python -m unittest discover -s tests
```

### Linter y Formato
```bash
uv run ruff check
uv run ruff format
```

### Desplegar en FastAPI Cloud
```bash
uv run fastapi deploy
```

---

## 🔒 Endpoints Principales

| Método | Endpoint | Descripción | Autenticación |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Información del servicio y enlaces a documentación | Pública |
| `GET` | `/health` / `/api/v1/health` | Estado de salud del servicio | Pública |
| `GET` | `/health/db` | Verificación de conectividad a la BD | Pública |
| `POST` | `/token` / `/api/v1/auth/token` | Login OAuth2 (compatible con Swagger UI) | Pública |
| `POST` | `/login` / `/api/v1/auth/login` | Login con cuerpo JSON (`email`, `password`) | Pública |
| `POST` | `/register` / `/api/v1/auth/register` | Registro público de nuevos usuarios | Pública |
| `GET` | `/me` / `/api/v1/auth/me` | Perfil del usuario autenticado actual | Bearer JWT |
| `GET` | `/users` / `/api/v1/users` | Listado paginado de usuarios (`skip`, `limit`) | Bearer JWT |
| `POST` | `/users` / `/api/v1/users` | Crear un nuevo usuario (administrativo) | Bearer JWT |
| `GET` | `/users/{id}` / `/api/v1/users/{id}` | Obtener usuario por UUID | Bearer JWT |
| `PUT` | `/users/{id}` / `/api/v1/users/{id}` | Actualizar datos de usuario | Bearer JWT |
| `DELETE` | `/users/{id}` / `/api/v1/users/{id}` | Eliminar usuario | Bearer JWT |

---

## ⚙️ Configuración y Variables de Entorno

Copia el archivo de ejemplo para configurar tu entorno local:

```bash
cp .env.example .env
```

Las variables admitidas en `.env`:

```env
# URL de conexión directa (recomendada, compatible con Supabase psycopg)
DATABASE_URL=postgresql+psycopg://postgres.vrgcgtgoxevlziyqzxjl:PASSWORD@aws-1-eu-west-1.pooler.supabase.com:5432/postgres

# O variables individuales:
# DB_HOST=aws-1-eu-west-1.pooler.supabase.com
# DB_PORT=5432
# DB_NAME=postgres
# DB_USER=postgres.vrgcgtgoxevlziyqzxjl
# DB_PASSWORD=...

# Pool de conexiones
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Seguridad JWT
JWT_SECRET_KEY=tu_clave_secreta_generada_aleatoriamente
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

Para generar una clave `JWT_SECRET_KEY` criptográficamente segura:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ☁️ Despliegue automático en FastAPI Cloud

El proyecto está vinculado a FastAPI Cloud mediante `.fastapicloud/cloud.json`.
Ese archivo contiene el `app_id`; no es necesario usar `team_id` en el workflow.
La carpeta `.fastapicloud` no debe subirse al repositorio.

Para configurar GitHub Actions desde cero, inicia sesión y ejecuta:

```bash
uv run fastapi cloud login
uv run fastapi cloud setup-ci --branch main
```

Esto crea `.github/workflows/deploy.yml`, que ejecuta `uv run fastapi deploy`
automáticamente cada vez que se hace push a `main`.

Secretos necesarios en GitHub (**Settings > Secrets and variables > Actions > Repository secrets**):

```text
FASTAPI_CLOUD_TOKEN   # Deploy token de FastAPI Cloud
FASTAPI_CLOUD_APP_ID  # ID de .fastapicloud/cloud.json
```

Las variables en producción (`DATABASE_URL`, `JWT_SECRET_KEY`, etc.) se configuran en el panel de **FastAPI Cloud**.
