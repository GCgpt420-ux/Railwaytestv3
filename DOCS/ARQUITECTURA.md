# Arquitectura del proyecto Tutor-PAES

## 1. Contexto general

Este repositorio es una aplicación full‑stack para administración y realización de evaluaciones tipo PAES. Contiene:
- Backend en Python (FastAPI u otro framework ASGI), con migraciones Alembic y scripts de seed.
- Frontend en Next.js (App Router) con React + TypeScript y Tailwind CSS.
- Orquestación mínima por `docker-compose` y ficheros de dependencias.

El frontend consume APIs REST expuestas por el backend; el backend gestiona persistencia, autenticación, lógica de negocio y llamadas a servicios de IA.

## 2. Contexto backend — carpetas y archivos clave

- [backend/app/main.py](backend/app/main.py)
  - Punto de entrada de la app (arranque, inclusión de routers y middlewares). Editar para añadir startup/shutdown o middleware.
- [backend/app/api/v1/endpoints/](backend/app/api/v1/endpoints/)
  - `auth.py`: endpoints de autenticación (login, refresh). Cambios aquí afectan el flujo de login y tokens.
  - `users.py`: CRUD y consultas de usuario. Editar para nuevos campos de perfil o validaciones.
  - `quiz.py`: endpoints para crear/obtener quizzes y enviar respuestas. Cambiar reglas de evaluación aquí.
  - `ai.py`: endpoints que delegan en servicios de IA. Modificar para ajustar prompts o proveedor.
  - `catalog.py`, `health.py`: catálogo de recursos y healthchecks.
- [backend/app/core/](backend/app/core/)
  - `config.py`: configuración por entorno (DB URL, keys). Actualizar para nuevos entornos o variables.
  - `auth.py`: lógica de autenticación (JWT, dependencias). Cambiar si se modifica la estrategia de tokens.
  - `exceptions.py`, `logging_config.py`: centralizan errores y logging.
- [backend/app/db/](backend/app/db/)
  - `models.py`: modelos ORM / tablas. Modificar para añadir/eliminar campos; luego crear migración.
  - `session.py`: motor y sessions DB.
- [backend/app/schemas/](backend/app/schemas/)
  - Schemas Pydantic (contratos request/response). Actualizar para cambios en la API.
- [backend/app/services/ai_service.py](backend/app/services/ai_service.py)
  - Encapsula llamadas a proveedores de IA y templates de prompt.
- `migrations/` y `alembic.ini`
  - Contienen scripts de migración; siempre actualizar al cambiar `models.py`.
- `requirements.txt`, `docker-compose.yml`
  - Dependencias y orquestación; editar para añadir servicios (ej. Redis) o cambiar versiones.
- `backend/scripts/seed_*.py`
  - Scripts para poblar datos de desarrollo.

### Qué editar para cambios comunes (backend)
- Cambiar contrato API: actualizar `schemas/`, los endpoints implicados y `models.py` si hay persistencia; añadir migración.
- Cambiar auth: editar `core/auth.py` y revisitar dependencias en `main.py` y tests.
- Cambiar proveedor IA o prompts: editar `services/ai_service.py`.

## 3. Contexto frontend — carpetas y archivos clave

- `tutor-paes-frontend/app/`
  - `layout.tsx`, `globals.css`: layout y estilos globales.
  - `page.tsx` y rutas (`/login`, `/dashboard`, `/quiz`, `/quiz/[subjectCode]`, `/admin/questions`): entradas de ruta.
  - Convención: páginas “delgadas” (delegan a vistas en `src/features/**/views`).
- `tutor-paes-frontend/src/features/` (feature-first)
  - `*/views/`: pantallas/flows completos (pueden manejar navegación, Suspense, guards).
  - `*/components/`: componentes reutilizables del feature.
  - Ejemplos:
    - `src/features/quiz/views/QuizFlowView.tsx` (orquestador del flujo)
    - `src/features/admin/questions/views/AdminQuestionsView.tsx` (pantalla admin)
- `tutor-paes-frontend/src/lib/api/`
  - Cliente HTTP y wrappers por dominio (`auth.ts`, `quiz.ts`, `dashboard.ts`, etc.).
  - Además existe `src/lib/api.ts` como punto de entrada/compatibilidad para algunos llamados.
- `tutor-paes-frontend/src/hooks/` y `src/features/**/hooks/`
  - Hooks compartidos (ej. `src/hooks/useQuiz.ts`) y hooks específicos por feature.
- `tutor-paes-frontend/src/components/`
  - `layout/Layout.tsx`: layout reutilizable.
  - `ui/`: componentes UI atómicos (Button/Card/Input/Badge, etc.).
- `package.json`, `next.config.ts`, `tailwind.config.ts`:
  - Configuración de build, scripts y tokens de diseño.

### Qué editar para cambios comunes (frontend)
- Cambiar contratos API: actualizar llamadas en `src/lib/api/*` y ajustar tipos en `src/types`.
- Cambiar navegación o UX del quiz: editar `src/hooks/useQuiz.ts` y vistas/componentes en `src/features/quiz/**`.
- Cambiar estilos globales o tokens: editar `globals.css` y `tailwind.config.ts`.

Notas de routing (quiz):
- Ruta canónica: `/quiz/[subjectCode]` (valida subjectCode).
- Ruta legacy: `/quiz` (valida y redirige a la ruta canónica).

> Nota: ver convención de frontend en `DOCS/FRONTEND_CONVENCIONES.md`.

## 4. Recomendaciones y futuros cambios (coherencia)

- Versionado de API: mantener rutas `/api/v1/` y crear `/api/v2/` para breaking changes. Actualizar SDKs/clients en frontend.
- Generar tipos desde OpenAPI: exponer OpenAPI en el backend y generar tipos/clients TypeScript para evitar divergencias.
- Tests y CI: añadir tests backend (pytest) y frontend (Jest + React Testing Library); integrar linters y formatters en CI.
- Convenciones y linters: aplicar `black`, `isort` en backend; `ESLint` + `Prettier` en frontend.
- Migraciones obligatorias: para cualquier cambio en `models.py`, crear migración Alembic y probar en staging.
- Gestión de secretos: usar variables de entorno o secret manager; no hardcodear keys en el repo.
- Observabilidad: agregar logging estructurado y health checks; considerar métricas y trazas.
- Encapsular IA: mantener prompts y llaves en `services/ai_service.py` y registrar uso/costos.

## 5. Enlaces rápidos (archivos referenciados)

- Backend main: [backend/app/main.py](backend/app/main.py)
- Endpoints: [backend/app/api/v1/endpoints/](backend/app/api/v1/endpoints/)
- Models DB: [backend/app/db/models.py](backend/app/db/models.py)
- Schemas: [backend/app/schemas/](backend/app/schemas/)
- IA service: [backend/app/services/ai_service.py](backend/app/services/ai_service.py)
- Migraciones: [backend/migrations/](backend/migrations/)
- Frontend entry (app): [tutor-paes-frontend/app/](tutor-paes-frontend/app/)
- Frontend API client: [tutor-paes-frontend/src/lib/api/client.ts](tutor-paes-frontend/src/lib/api/client.ts)
- Frontend quiz API: [tutor-paes-frontend/src/lib/api/quiz.ts](tutor-paes-frontend/src/lib/api/quiz.ts)
- Frontend hooks: [tutor-paes-frontend/src/hooks/useQuiz.ts](tutor-paes-frontend/src/hooks/useQuiz.ts)
- Componentes UI: [tutor-paes-frontend/src/components/ui/](tutor-paes-frontend/src/components/ui/)


