# Project Tree (limpio) + Contexto

Este archivo resume la estructura principal del repo **sin** incluir carpetas generadas/temporales/caché (por ejemplo: `.venv`, `node_modules`, `.next`, `__pycache__`, `.runtime`, `coverage`, logs, pids, etc.).

## Backend (FastAPI) — `backend/`

### Tree (filtrado)

```text
backend/
  .dockerignore
  .env.example
  Dockerfile
  alembic.ini
  docker-compose.yml
  railway.json
  requirements.txt
  app/
    __init__.py
    main.py
    api/
      __init__.py
      v1/
        __init__.py
        endpoints/
          __init__.py
          ai.py
          auth.py
          catalog.py
          health.py
          questions.py
          quiz.py
          users.py
    core/
      __init__.py
      auth.py
      config.py
      exceptions.py
      logging_config.py
    db/
      __init__.py
      base.py
      models.py
      session.py
    schemas/
      __init__.py
      errors.py
      questions.py
      quiz.py
      quiz_completion.py
    services/
      __init__.py
      ai_service.py
  migrations/
    README
    env.py
    requirements.txt
    script.py.mako
    versions/
      1fe2ecfae783_attempt_completion_fields.py
      70130b097505_add_reading_text_to_questions.py
      7140ca6c3d65_init_schema.py
      787db5040a31_init_schema.py
      b3a1f0c2d9e4_add_is_admin_to_users.py
      dd63e36c7aa1_add_exam_tables.py
  scripts/
    __init__.py
    seed_paes.py
    seed_questions.py
    seed_user.py
```

### Qué es cada parte (1 línea)

- `app/main.py`: crea la app FastAPI, configura CORS/logging/lifespan y registra routers `/api/v1/*`.
- `app/api/v1/endpoints/*`: capa HTTP (routers) por dominio (auth, quiz, questions, health, etc.).
- `app/core/config.py`: settings por env (Pydantic), normaliza `DATABASE_URL`, define CORS/JWT/log.
- `app/core/auth.py`: helpers de seguridad (JWT, hashing, dependencias auth).
- `app/core/exceptions.py`: excepciones propias + forma estándar de errores.
- `app/core/logging_config.py`: logging centralizado.
- `app/db/session.py`: engine/sesión SQLAlchemy (conexión DB).
- `app/db/models.py`: modelos ORM (tablas).
- `app/db/base.py`: `Base` declarativa y registro común.
- `app/schemas/*`: contratos Pydantic (request/response) para el API.
- `app/services/ai_service.py`: lógica de negocio para la parte AI (separada de endpoints).
- `migrations/`: Alembic (migraciones de base de datos).
- `scripts/seed_*.py`: seeds idempotentes para demo local.

## Frontend (Next.js App Router) — `tutor-paes-frontend/`

### Tree (filtrado)

```text
tutor-paes-frontend/
  .gitignore
  eslint.config.mjs
  frontend_texts.md
  next.config.ts
  package-lock.json
  package.json
  postcss.config.mjs
  tailwind.config.ts
  tsconfig.json
  vitest.config.ts
  .storybook/
    main.ts
    preview.tsx
    storybook.css
  public/
    favicon.svg
    file.svg
    globe.svg
    next.svg
    vercel.svg
    window.svg
  app/
    globals.css
    layout.tsx
    page.tsx
    error.tsx
    not-found.tsx
    login/
      page.tsx
    dashboard/
      page.tsx
    quiz/
      [subjectCode]/
        page.tsx
    admin/
      questions/
        page.tsx
  scripts/
    sync-tokens.mjs
  src/
    api/
      client.ts
      errors.ts
      index.ts
      services/
        ai.service.ts
        auth.service.ts
        dashboard.service.ts
        questions.service.ts
        quiz.service.ts
        index.ts
    components/
      layout/
        Layout.tsx
        PageContainer.tsx
      shared/
        ErrorAlert.tsx
        LoadingSpinner.tsx
        RecoverableError.test.tsx
        RecoverableError.tsx
    core/
      hooks/
        index.ts
        useRequireAdmin.ts
        useRequireAuth.ts
      tokens/
        index.ts
        tokens.schema.md
        tokens.ts
      ui/
        Badge.stories.tsx
        Badge.tsx
        Button.stories.tsx
        Button.tsx
        Card.stories.tsx
        Card.tsx
        Input.stories.tsx
        Input.tsx
        Spinner.stories.tsx
        Spinner.tsx
        index.ts
    features/
      admin/
        questions/
          views/
            AdminQuestionsView.tsx
          index.ts
      auth/
        components/
          AuthEventsProvider.tsx
        views/
          LoginView.tsx
        index.ts
      dashboard/
        components/
          SubjectCard.tsx
        views/
          DashboardContentView.tsx
          DashboardPageView.tsx
        index.ts
      landing/
        views/
          LandingView.tsx
        index.ts
      quiz/
        components/
          ChoiceButton.tsx
          ChoiceButton.stories.tsx
          ChoiceButton.test.tsx
          FeedbackDisplay.tsx
          QuestionDisplay.tsx
          QuizTopBar.tsx
          QuizTopBar.stories.tsx
          TopicCompletedScreen.tsx
        hooks/
          useQuiz.ts
        mappers/
          completionMapper.ts
          feedbackMapper.ts
          questionMapper.ts
          index.ts
        views/
          QuizFlowView.tsx
        index.ts
    lib/
      auth/
        jwt.ts
        session.ts
        storage.ts
      quiz/
        lastTopic.ts
        lastTopic.test.ts
        subjects.ts
    styles/
      tokens.test.ts
    test/
      setup.ts
    types/
      index.ts
      schema.ts
      domain/
        attempt.ts
        feedback.ts
        index.ts
        question.ts
```

### Qué es cada parte (1 línea)

- `app/*`: rutas Next.js (App Router) — puntos de entrada que importan vistas/features.
- `src/core/ui/*`: UI atómica y pura (Button/Input/Card/Badge/Spinner) + stories.
- `src/core/tokens/*`: tokens sincronizados desde Tailwind (`tokens:sync` / `tokens:check`).
- `src/api/*`: cliente HTTP y helpers de errores.
- `src/api/services/*`: llamadas al backend (por dominio).
- `src/features/*`: lógica por dominio (views, components, mappers).
- `src/components/layout/*`: layout compartido.
- `src/components/shared/*`: componentes compartidos de negocio (errores/loading).
- `src/core/hooks/*`: hooks globales/guards (auth/admin).
- `src/features/*/hooks/*`: hooks específicos de dominio (ej. quiz).
- `src/types/*`: tipos del dominio y schemas.
- `scripts/sync-tokens.mjs`: sincroniza tokens desde `tailwind.config.ts`.
