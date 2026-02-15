# Mapa del proyecto — TutorPAES v2

Objetivo: que puedas explicar el proyecto en 5–10 minutos (qué hace, cómo fluye, dónde está cada cosa) sin tener que “recordar todo”.

---

## 1) Arquitectura (alto nivel)

- Frontend: Next.js (App Router) en `tutor-paes-frontend/`
- Backend: FastAPI + SQLAlchemy + Alembic en `backend/`
- DB: Postgres (docker-compose en `backend/docker-compose.yml`)

Flujo base:

1) Frontend obtiene `access_token` con `POST /api/v1/auth/login`
2) Frontend usa `Authorization: Bearer <token>` en llamadas protegidas
3) Backend valida token (JWT) → obtiene user desde DB
4) Endpoints operan sobre modelos SQLAlchemy (Attempt, Question, etc.)

---

## 2) Backend — entrypoint y routers

### 2.1 App principal
- Punto de entrada: `backend/app/main.py`
  - Configura CORS
  - Incluye routers con prefijo `/api/v1`
  - En lifespan crea tablas si faltan (`Base.metadata.create_all`) — útil en dev, pero en prod normalmente se prefiere solo Alembic.

### 2.2 Routers incluidos
En `backend/app/main.py` se incluyen:

- Health: `backend/app/api/v1/endpoints/health.py`
- Auth: `backend/app/api/v1/endpoints/auth.py`
- Catalog: `backend/app/api/v1/endpoints/catalog.py`
- Quiz: `backend/app/api/v1/endpoints/quiz.py`
- Users: `backend/app/api/v1/endpoints/users.py`
- Questions (admin): `backend/app/api/v1/endpoints/questions.py`

---

## 3) Backend — Auth (JWT) y Admin

### 3.1 JWT: cómo se autentica
Archivo: `backend/app/core/auth.py`

- `create_access_token(user_id)` crea JWT con `sub=str(user_id)`, `exp`, `iat`.
- `get_current_user()`:
  - lee header `Authorization: Bearer <token>`
  - decodifica y extrae `user_id`
  - hace query a DB por `User.id == user_id`
  - retorna el `User` completo (DB-backed)

### 3.2 Admin gate (persistido, no heurístico)
- `require_admin_user()` permite acceso solo si `user.is_admin == True`
- La columna `users.is_admin` existe por migración.

---

## 4) Backend — Quiz (motor principal)

Archivo: `backend/app/api/v1/endpoints/quiz.py`

### 4.1 `GET /api/v1/quiz/next-question`
- Responde una unión discriminada:
  - `{ kind: "question", ... }`
  - `{ kind: "topic_completed", ... }`
- Encuentra attempt en progreso (si existe) y evita repetir preguntas usando `attempt_feedback`.
- Cuando ya no quedan preguntas:
  - marca attempt `completed`
  - calcula score
  - retorna `kind: topic_completed`

Extra:
- Soporta `attempt_id` opcional para pedir el cierre de un attempt específico (útil con cierre robusto del POST /answer).

### 4.2 `POST /api/v1/quiz/answer`
- Requiere JWT; `user_id` se deriva del token.
- Deduplica respuestas por `(attempt_id, question_id)` devolviendo el feedback existente.
- **Cierre robusto del attempt**:
  - tras guardar feedback, verifica si quedan preguntas sin responder
  - si no quedan, marca attempt como `completed` y devuelve `is_attempt_finished: true`

---

## 5) Backend — Questions (Admin)

Archivo: `backend/app/api/v1/endpoints/questions.py`

- Router aplica dependencia global admin:
  - `dependencies=[Depends(require_admin_user)]`
- Endpoints:
  - `POST /api/v1/questions/` crea pregunta + choices
  - `GET /api/v1/questions/recent` lista últimas preguntas

---

## 6) Backend — Modelos DB (SQLAlchemy)

Archivo: `backend/app/db/models.py`

Entidades clave para explicar el MVP:

- `User`: `email`, `phone`, `is_active`, `is_admin`
- `Exam`, `Subject`, `Topic`: catálogo PAES
- `Question`, `QuestionChoice`: banco de preguntas
- `Attempt`: intento del usuario por topic (status, score)
- `AttemptFeedback`: respuesta por pregunta dentro de un attempt

---

## 7) Frontend — estructura útil

Raíz: `tutor-paes-frontend/`

### 7.1 API client
Carpeta: `tutor-paes-frontend/src/lib/api/`

- `client.ts`: `API_BASE_URL` + `handleResponse()` (convierte errores HTTP en excepción)
- `auth.ts`, `quiz.ts`, `dashboard.ts`, `questions.ts`, `ai.ts`: llamadas a backend
- Patrón: `getAuthHeaders()` lee `localStorage.access_token` y añade `Authorization`.

### 7.2 Hook del quiz
Archivo: `tutor-paes-frontend/src/hooks/useQuiz.ts`

- Orquesta:
  - `startAttempt()` → llama `getNextQuestion`
  - `submitAnswer()` → llama `POST /quiz/answer`
  - `proceedToNext()` → si `is_attempt_finished=true` pide cierre por `attempt_id` y muestra pantalla final

### 7.3 Vista del flujo
Archivo: `tutor-paes-frontend/src/features/quiz/views/QuizFlowView.tsx`

- Renderiza:
  - pantalla de pregunta
  - pantalla de feedback
  - pantalla final (`TopicCompletedScreen`)

---

## 8) Dónde mirar según la pregunta

- “¿Dónde se valida el token?” → `backend/app/core/auth.py`
- “¿Cómo se define admin?” → `User.is_admin` en `models.py` + `require_admin_user`
- “¿Por qué un attempt termina?” → `quiz.py` (GET next-question + POST answer)
- “¿Qué llama el frontend exactamente?” → `src/lib/api/*.ts` + `src/hooks/useQuiz.ts`
- “¿Cómo se levanta local?” → `README.md` + `backend/docker-compose.yml`
