# Contexto general — TutorPAES v2

TutorPAES v2 es un proyecto full‑stack para practicar contenidos tipo PAES con un flujo de quiz por materia/tema, feedback inmediato y seguimiento de progreso.

## Stack

- Backend: FastAPI + SQLAlchemy + Alembic + PostgreSQL
- Frontend: Next.js (App Router) + React + TypeScript + TailwindCSS
- API base: `/api/v1`

## Flujos principales

- Login: obtiene JWT (modo demo: solo email).
- Dashboard: muestra materias/temas y enruta a quiz.
- Quiz: obtiene pregunta → envía respuesta → muestra feedback → avanza → completa tópico.
- Admin preguntas: crear pregunta y ver “recent” (JWT requerido).

## Árbol resumido del repo

### Backend

```
backend/
  alembic.ini
  docker-compose.yml
  requirements.txt
  app/
    main.py
    api/v1/endpoints/
      auth.py
      quiz.py
      users.py
      questions.py
      health.py
    core/
    db/
    schemas/
    services/
  migrations/
  scripts/
```

### Frontend

```
tutor-paes-frontend/
  app/
    login/page.tsx
    dashboard/page.tsx
    quiz/page.tsx
    quiz/[subjectCode]/page.tsx
    admin/questions/page.tsx
  src/
    features/
      quiz/views/QuizFlowView.tsx
      dashboard/views/DashboardPageView.tsx
      admin/questions/views/AdminQuestionsView.tsx
    lib/api/
    hooks/
    types/
```

## Routing del quiz (regla actual)

- Ruta canónica: `/quiz/[subjectCode]`.
- Ruta legacy: `/quiz` valida parámetros y redirige a la ruta canónica.
- `subjectCode` válido: `M1 | M2 | LECT | CIEN | HIST`.

## Variables de entorno relevantes

Backend (ejemplo: `backend/.env`):
- `DATABASE_URL`
- `SECRET_KEY`
- `CORS_ORIGINS`
- `DEMO_EMAIL`

Frontend (ejemplo: `tutor-paes-frontend/.env.local`):
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_DEMO_EMAIL`
- `NEXT_PUBLIC_ENABLE_QUIZ_MOCKS` (si existe, habilita mocks controlados)
