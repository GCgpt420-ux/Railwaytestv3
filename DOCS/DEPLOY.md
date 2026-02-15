# Deploy: convertir el proyecto en un link (MVP)

Este documento describe un camino simple y realista para publicar el MVP:
- Frontend (Next.js) en Vercel
- Backend (FastAPI) en Railway/Render/Fly
- Postgres en Neon/Supabase/Render

No es el único camino, pero es el más rápido con buen DX.

---

## 0) Pre-requisitos

- Repositorio en GitHub (o GitLab)
- Variables de entorno separadas para Front y Back
- Base de datos Postgres accesible desde Internet

---

## 1) Backend (FastAPI)

### Opción 0 (rápida): Railway (Python)

Railway suele entregar `DATABASE_URL` como `postgresql://...` (o `postgres://...`).
Este repo normaliza automáticamente esa URL a `postgresql+psycopg://...` para SQLAlchemy.

1) Sube el repo a GitHub.
2) En Railway:
  - New Project → Deploy from GitHub Repo
  - Root directory: `backend/` (o configura el servicio para apuntar a esa carpeta)
  - Nota: este repo incluye `backend/railway.json` (config-as-code) con el `startCommand` y healthcheck.
    Para que Railway lo use, el servicio debe apuntar a `backend/` como Root Directory.
3) Variables de entorno mínimas:
  - `DATABASE_URL` (la de Railway Postgres o Neon)
  - `SECRET_KEY` (openssl rand -hex 32)
  - `CORS_ORIGINS` (incluye el dominio de Vercel, separado por comas)
  - `AUTO_CREATE_TABLES=false`
4) Start command:
  - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5) Migraciones:
  - Corre `alembic upgrade head` apuntando a la DB remota (one-off) antes de usar el MVP.

#### Si falla el build con "Error creating build plan with Railpack"

Eso suele pasar cuando Railway intenta construir desde la raíz del repo (monorepo) y no encuentra un proyecto Python.

Soluciones:
- En el servicio de Railway, configura **Root Directory = `backend/`**.
- Alternativa: usa el `Dockerfile` dentro de `backend/` (Railway puede construir vía Dockerfile si lo detecta en el root del servicio).

### Opción A: Render (Python Web Service)

1) Sube el repo a GitHub.
2) Crea un servicio web en Render apuntando a la carpeta `backend/`.
3) Configura:
- Build command:
  - `pip install -r requirements.txt`
- Start command:
  - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4) Variables de entorno recomendadas:
- `DATABASE_URL` (de Neon/Supabase/etc.)
- `SECRET_KEY` (openssl rand -hex 32)
- `CORS_ORIGINS` (incluye el dominio de Vercel)
- `AUTO_CREATE_TABLES=false`

5) Migraciones:
- Ideal: correr `alembic upgrade head` como “one-off job” en Render (o desde tu máquina apuntando a la DB remota).

### Opción B: Fly.io (con Docker)

Si quieres Fly, lo mejor es agregar un `Dockerfile` para backend (post-deadline si estás corto de tiempo).

---

## 2) DB (Postgres)

### Opción recomendada: Neon

- Crea un proyecto Neon
- Copia el connection string (Postgres URL)
- Pégalo en `DATABASE_URL`

Checklist:
- Habilitar backups/snapshots (si el plan lo permite)
- Crear un usuario con permisos mínimos (post-deadline)

---

## 3) Frontend (Next.js)

### Vercel

1) Importa el repo en Vercel.
2) Selecciona el subdirectorio: `tutor-paes-frontend/`.
3) Variables de entorno:
- `NEXT_PUBLIC_API_BASE_URL=https://<tu-backend>`
- `NEXT_PUBLIC_DEMO_EMAIL=demo@example.com`
- `NEXT_PUBLIC_ENABLE_QUIZ_MOCKS=false`

4) Deploy.

---

## 4) Operación mínima (para “no tener miedo”)

### 4.1 Healthcheck
- Backend ya tiene health endpoint (ver tag `health`).
- Configura el proveedor (Render/Vercel) para monitorear `/api/v1/health/`.

### 4.2 Logs
- Revisa logs del backend en el provider.
- Para bugs, usa el campo `error` del `ErrorOut` como clave.

### 4.3 Seguridad mínima
- `SECRET_KEY` fuerte y privado.
- `CORS_ORIGINS` restringido al dominio real del frontend.
- No activar mocks en prod (`NEXT_PUBLIC_ENABLE_QUIZ_MOCKS=false`).
- Mantener `AUTO_CREATE_TABLES=false` en prod.

---

## 5) Checklist de release (Feb 15)

- Backend responde `/docs` y `/api/v1/health/`.
- Login devuelve token y el frontend lo usa.
- Quiz: completa tema y el attempt queda `completed`.
- Admin:
  - token normal => 403 en `/questions/*`
  - token admin => 200 y permite `POST /questions/bulk`
- Seeds/migraciones documentadas.
