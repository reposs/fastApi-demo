# fastApi-demo

Demo online: https://fastapi-demo-1373c10f.fastapicloud.dev/

Documentación de la API: https://fastapi-demo-1373c10f.fastapicloud.dev/docs

# Run project PRO

`uv run fastapi run`

# Run project DEV

`uv run fastapi dev`

# Run deploy project (FastapiCLOUD)

`uv run fastapi deploy`

# Despliegue automático en FastAPI Cloud

El proyecto está vinculado a FastAPI Cloud mediante `.fastapicloud/cloud.json`.
Ese archivo contiene el `app_id`; no es necesario usar `team_id` en el workflow.
La carpeta `.fastapicloud` no debe subirse al repositorio.

Para configurar GitHub Actions desde cero, inicia sesión y ejecuta:

```bash
uv run fastapi cloud login
uv run fastapi cloud setup-ci --branch main
```

Esto crea `.github/workflows/deploy.yml`, que ejecuta `uv run fastapi deploy`
automáticamente cada vez que se hace push a `main`. Después, guarda el workflow:

```bash
git add .github/workflows/deploy.yml
git commit -m "Configure automatic FastAPI Cloud deployment"
git push origin main
```

Si hay que renovar el token sin crear otro workflow, ejecuta:

```bash
uv run fastapi cloud setup-ci --secrets-only
```

El workflow necesita estos secretos en GitHub, en **Settings > Secrets and
variables > Actions > Repository secrets**:

```text
FASTAPI_CLOUD_TOKEN   # Deploy token de FastAPI Cloud
FASTAPI_CLOUD_APP_ID  # ID de .fastapicloud/cloud.json
```

El token solo se muestra al crearlo. Si se pierde, hay que generar uno nuevo.
No debe guardarse en el código ni en el README.

Las variables que necesita la aplicación en producción se configuran en
FastAPI Cloud, no en GitHub Actions:

```text
DATABASE_URL
JWT_SECRET_KEY
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

La demo pública está disponible en:

https://fastapi-demo-1373c10f.fastapicloud.dev/

La documentación interactiva está en:

https://fastapi-demo-1373c10f.fastapicloud.dev/docs

# Add EmailStr validator

`uv add email-validator`

# Add SQLModel

`uv add sqlmodel`

# Database connection

`app/core/db/database.py` usa SQLAlchemy para conectarse a Supabase mediante
variables de entorno. Crea un archivo `.env` en la raíz del proyecto usando
`.env.example` como referencia. La opción recomendada es definir la URL completa:

```bash
export DATABASE_URL='postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres'
```

En PowerShell:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres"
```

También se pueden definir por separado:

```text
DB_HOST=aws-1-eu-west-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.vrgcgtgoxevlziyqzxjl
DB_PASSWORD=...
```

Añade también la configuración JWT. Genera una clave segura con:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Guárdala en `.env` como `JWT_SECRET_KEY=...` y no la compartas.

Instala las dependencias si aún no están instaladas:

```bash
uv add "psycopg[binary]" python-dotenv
```

El endpoint `POST /token` espera un formulario con los campos `email` y
`password`. Para el usuario inicial, usa `johndoe@example.com` como email. La tabla
`users` debe tener las columnas `id`, `created_at`, `firstname`, `lastname`,
`email` y `password`; `password` debe contener un hash Argon2 generado con
`pwdlib`, no la contraseña en texto plano.
