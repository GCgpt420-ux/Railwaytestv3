# Comandos de desarrollo — TutorPAES v2

> Objetivo: tener una lista única de comandos (ordenados) para levantar DB + backend + frontend, probar endpoints y hacer build.

## ✅ Forma canónica (recomendado)

Levantar todo (DB + migraciones + seeds + backend + frontend):

```bash
./scripts/dev-up.sh
```

Smoke test (validación mínima):

```bash
./scripts/smoke-demo.sh
```

Logs/PIDs (runtime):
- `.runtime/backend.uvicorn.log` / `.runtime/backend.uvicorn.pid`
- `.runtime/frontend.next-dev.log` / `.runtime/frontend.next-dev.pid`

Apagar todo:

```bash
./scripts/dev-down.sh
```

> El resto de este documento deja los pasos manuales equivalentes.

## 0) Ubicación (root)

```bash
cd /home/gcuevas/ia_bot_v2
```

---

## 1) Base de datos (Postgres via Docker)

### 1.1 Levantar Postgres en segundo plano

```bash
cd backend
docker compose up -d
```

### 1.2 Ver estado del contenedor

```bash
docker compose ps
```

### 1.3 Ver logs del Postgres (si hay problemas)

```bash
docker compose logs -f db
```

### 1.4 Apagar Postgres

```bash
docker compose down
```

> Nota: este `docker-compose.yml` solo levanta Postgres (puerto `5432`). No controla el puerto `8000`.

---

## 2) Backend (FastAPI)

### 2.1 Crear venv (solo la primera vez)

```bash
cd backend
python3 -m venv .venv
```

### 2.2 Activar venv

```bash
cd backend
. .venv/bin/activate
```

### 2.3 Instalar dependencias del backend

```bash
cd backend
. .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2.4 Verificar que la app importa bien (sanity check)

```bash
cd backend
. .venv/bin/activate
python -c "from app.main import app; print('app ok')"
```

### 2.5 Ver si el puerto 8000 está ocupado

```bash
ss -ltnp | grep ':8000' || true
```

### 2.6 Levantar backend en puerto 8000 (recomendado)

```bash
cd backend
. .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2.7 Si 8000 está ocupado, usar 8001 (alternativa)

```bash
cd backend
. .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

## 3) Frontend (Next.js)

### 3.1 Instalar dependencias

```bash
cd tutor-paes-frontend
npm install
```

### 3.2 Configurar URL del backend (si aplica)

- Por defecto el frontend usa `NEXT_PUBLIC_API_BASE_URL`.
- Crea/edita `tutor-paes-frontend/.env.local`:

```bash
# dentro de tutor-paes-frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

> Si levantaste backend en `8001`, usa `http://localhost:8001`.

### 3.3 Levantar frontend en modo dev

```bash
cd tutor-paes-frontend
npm run dev
```

### 3.4 Build de producción (verifica que compila)

```bash
cd tutor-paes-frontend
npm run build
```

### 3.5 Correr build (preview prod)

```bash
cd tutor-paes-frontend
npm run start
```

### 3.6 Tokens (Tailwind ↔ runtime TS)

La fuente de verdad de tokens es `tutor-paes-frontend/tailwind.config.ts`.
El archivo `tutor-paes-frontend/src/styles/tokens.ts` se auto-genera para poder usar tokens en TS (tests/stories/UI).

Validar que está sincronizado (recomendado en PRs):

```bash
cd tutor-paes-frontend
npm run tokens:check
```

Regenerar `tokens.ts` desde Tailwind:

```bash
cd tutor-paes-frontend
npm run tokens:sync
```

### 3.7 Tests (frontend)

```bash
cd tutor-paes-frontend
npm test
```

### 3.8 Storybook (QA visual)

Levantar Storybook en dev:

```bash
cd tutor-paes-frontend
npm run storybook
```

Modo “igual que la app” (carga `app/globals.css`):

```bash
cd tutor-paes-frontend
STORYBOOK_FULL_UI=1 npm run storybook
```

Build estático (útil para CI):

```bash
cd tutor-paes-frontend
npm run build-storybook
```

Build estático “igual que la app”:

```bash
cd tutor-paes-frontend
STORYBOOK_FULL_UI=1 npm run build-storybook
```

---

## 4) Pruebas rápidas de endpoints (curl)

> Ajusta `8000`/`8001` según el puerto real del backend.

### 4.1 Health

```bash
curl -sS http://localhost:8000/api/v1/health/
```

### 4.2 Login (obtiene JWT)

```bash
curl -sS -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com"}'
```

> Nota: si vas a correr seeds, usa `python -m scripts.seed_*` (no `python scripts/*.py`) para que los imports `from app...` funcionen sin tocar PYTHONPATH.

### 4.3 Extraer token (manual)

Copia el campo `access_token` del JSON anterior. Luego úsalo así:

```bash
export TOKEN='PEGA_AQUI_EL_TOKEN'
```

### 4.4 Crear pregunta (Admin) — requiere token

```bash
curl -sS -X POST http://localhost:8000/api/v1/questions/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "subject_code":"M1",
    "topic_code":"ALG",
    "prompt":"Si 2x = 8, ¿cuál es el valor de x?",
    "reading_text":null,
    "explanation":"Despejar x dividiendo ambos lados por 2.",
    "difficulty":1,
    "choices":[
      {"label":"A","text":"2"},
      {"label":"B","text":"4"},
      {"label":"C","text":"6"},
      {"label":"D","text":"8"}
    ],
    "correct_choice":"B"
  }'
```

### 4.5 Listar preguntas recientes (Admin) — requiere token

```bash
curl -sS -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/api/v1/questions/recent?limit=10'
```

---

## 5) Operación (limpieza / troubleshooting)

### 5.1 Ver qué proceso ocupa un puerto

```bash
ss -ltnp | grep ':8000' || true
ss -ltnp | grep ':3000' || true
```

### 5.2 Matar proceso por PID (si sabes el PID)

```bash
kill -9 <PID>
```

### 5.3 Resetear DB (¡borra datos!)

```bash
cd backend
docker compose down -v
```

---

## 6) Notas importantes

- El `docker compose` del repo solo maneja Postgres; el backend se corre con `uvicorn` (venv).
- Si el sistema te bloquea `pip install` global (PEP 668), usa el venv (`backend/.venv`).
- Para endpoints admin, el backend exige `Authorization: Bearer <JWT>`.
