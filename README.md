# Run project PRO

`uv run fastapi run`

# Run project DEV

`uv run fastapi dev`

# Run deploy project (FastapiCLOUD)

`uv run fastapi deploy`

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
