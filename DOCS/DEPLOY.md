# Deploy: convertir el proyecto en un link (MVP)

Este documento describe el camino para publicar el MVP con configuración separada:
- **Frontend (Next.js)** en Vercel
- **Backend (FastAPI)** en Railway
- **Database (Postgres)** en Railway o Neon

---

## Arquitectura de Deploy

```
GitHub (Railwaytestv3) 
├── backend/ → Railway (FastAPI + Postgres)
└── front-end/tutor-ia-paes/ → Vercel (Next.js)
```

---

## 0) Pre-requisitos

- Repositorio en GitHub: https://github.com/GCgpt420-ux/Railwaytestv3
- Acceso a Railway (https://railway.app)
- Acceso a Vercel (https://vercel.com)
- Variables de entorno separadas para cada servicio

---

## 1) Backend en Railway (FastAPI + Python)

### Configuración automática con `railway.json`

El proyecto ahora incluye configuración en:
- `/railway.json` (raíz del repo) - especifica el contexto del backend
- `/backend/railway.json` - usa Dockerfile para build
- `/backend/Dockerfile` - construcción del contenedor

### Pasos de deploy:

1. **Crear servicio en Railway:**
   - Ve a https://railway.app
   - `+ New Project` → `Deploy from GitHub`
   - Conecta el repo `Railwaytestv3`
   - Railway detectará automáticamente el `Dockerfile` en `backend/`

2. **Configurar base de datos:**
   - En Railway, agrega un servicio `PostgreSQL`
   - Railway automáticamente expone `DATABASE_URL` como variable de entorno

3. **Variables de entorno en Railway:**
   ```
   DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
   SECRET_KEY=<generar con: openssl rand -hex 32>
   CORS_ORIGINS=https://tutor-ia-paes-*.vercel.app
   LOG_LEVEL=INFO
   AUTO_CREATE_TABLES=false
   ```

4. **Primera ejecución:**
   - Las migraciones corren automáticamente en el startup (ver `Dockerfile` CMD)
   - El Dockerfile ejecuta: `alembic upgrade head && uvicorn app.main:app ...`

5. **Health check:**
   - Railway usará `/api/v1/health/` para verificar que el servicio está listo

### Solución de problemas en Railway

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
