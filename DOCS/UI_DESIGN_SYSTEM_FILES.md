# Plan y lista de archivos para construir el Design System (UI)

Objetivo
- Dar una lista priorizada de componentes presentacionales y un plan mínimo para consolidarlos en un Design System (DS). Incluiré recomendaciones para prop-types/TS interfaces, tokens, testing y pasos de integración.

Resumen del estado actual (rápido)
- La lógica core está centralizada y razonablemente sólida: `useQuiz` (máquina de estados), `apiFetch`/`APIError`, y el backend tienen validaciones y protecciones recientes.
- Tests unitarios y build frontend pasan en el entorno local.
- Hay componentes presentacionales ya existentes y un pequeño conjunto de `ui/*` primitives (`Button`, `Input`, `Card`, `Badge`). Estos son el punto de partida natural para el DS.

Prioridad (qué extraer primero)
1. `Button` (base): base para acciones en toda la app.
2. `ChoiceButton` / `QuestionDisplay` presentational bits: componentes de alta prioridad para quiz.
3. `QuizTopBar`, `LoadingSpinner`, `ErrorAlert` / `RecoverableError`.
4. Form primitives: `Input` y cualquier control de formulario usado en login/admin.
5. Layout primitives: `Card`, `Badge` y `Layout` (shell app).

Archivo(s) necesarios (lista y rol)
- Primitives (base del DS)
  - tutor-paes-frontend/src/components/ui/Button.tsx — botón estilizado y accesible (variant/size/isLoading).
  - tutor-paes-frontend/src/components/ui/Input.tsx — control de input reutilizable.
  - tutor-paes-frontend/src/components/ui/Card.tsx — contenedor visual reutilizable.
  - tutor-paes-frontend/src/components/ui/Badge.tsx — estado/pill.

- Common / Presentational (migrar al DS)
  - tutor-paes-frontend/src/components/common/LoadingSpinner.tsx — indicador de carga.
  - tutor-paes-frontend/src/components/common/ErrorAlert.tsx — alerta visual de error.
  - tutor-paes-frontend/src/components/common/RecoverableError.tsx — wrapper UX de error + CTA.
  - tutor-paes-frontend/src/components/layout/Layout.tsx — shell/layout de la app.

- Feature-specific presentational (refactor: mover a DS cuando sean genéricos)
  - tutor-paes-frontend/src/features/quiz/components/ChoiceButton.tsx — alternativa de pregunta (mover a DS si es genérico o mantener en feature si específico).
  - tutor-paes-frontend/src/features/quiz/components/QuestionDisplay.tsx — orquestador local de UI de pregunta (mantener en feature, extraer subcomponentes presentacionales a DS).
  - tutor-paes-frontend/src/features/quiz/components/FeedbackDisplay.tsx — presentación de feedback (posible extracción parcial).
  - tutor-paes-frontend/src/features/quiz/components/QuizTopBar.tsx — candidato a componente DS (topbar/steps/progress).
  - tutor-paes-frontend/src/features/quiz/components/TopicCompletedScreen.tsx — pantalla de resumen (mantener en feature, extraer cards/tokens).

- Admin / Dashboard small components
  - tutor-paes-frontend/src/features/dashboard/components/SubjectCard.tsx — ejemplo de card reutilizable.

Infra y helpers a revisar/normalizar (no UI pero influyen en UX)
- tutor-paes-frontend/src/hooks/useQuiz.ts — máquina de estado del quiz (ya endurecida); mantener API estable al refactorizar UI.
- tutor-paes-frontend/src/lib/api/client.ts — `apiFetch` y `APIError` (central para error handling).
- tutor-paes-frontend/src/lib/api/errors.ts — helpers `isRetryableError/getErrorMessage`.
- tutor-paes-frontend/src/lib/quiz/lastTopic.ts — persistencia localStorage (no UI pero UX relevante).

Recomendaciones de diseño del DS
- Tokens: definir colores, radios, espacios y tipografía en variables Tailwind (o CSS variables) y documentarlos.
- Props contract: cada primitive debe exponer `className`, `variant`, `size`, `isLoading`, `disabled` y ser `forwardRef` compatible.
- Accessibility: testa `Button`, `ChoiceButton` y `Input` para `aria` roles y keyboard navigation.
- Storybook / Visual tests: levantar Storybook para componentes extraídos y añadir snapshots o Chromatic.
- Testing: unit tests para primitives y visual regression para componentes críticos (ChoiceButton / TopBar / Error states).
- Theming: considerar `tailwind.config.js` como fuente única de tokens y exponer utilidades para devs.

Plan mínimo de extracción (pasos)
1. Normalizar primitives: aislar `Button`, `Input`, `Card`, `Badge` en `src/components/ui/` y asegurar su API y tests.
2. Extraer `LoadingSpinner`, `ErrorAlert`, `RecoverableError` a `src/components/common/` (si no están ya). Añadir tests y ejemplos.
3. Refactorizar `ChoiceButton` y subcomponentes de `QuestionDisplay` para usar `Button` y `Card` primitives.
4. Documentar y crear stories (Storybook) para cada primitive.
5. Revisar `useQuiz` API surface: exponer funciones `startAttempt`, `submitAnswer`, `proceedToNext`, `retry` de forma estable para UI.
6. Reemplazar usos en features por los componentes del DS y eliminar duplicados.

Checklist de criterios "Listo" antes de pulir visuales
- Primitives tienen tests + stories.
- UI features (quiz) usan primitives sin APIs ad-hoc.
- No reglas inline de colores/espacios que rompan tokens.
- Error handling uniforme (uso de `RecoverableError`) y mensajes localizables.

Siguientes acciones que puedo realizar ahora
- Generar un PR/branch con la extracción de `ChoiceButton` → `src/components/ui/ChoiceButton` (pequeño PR iterativo).
- Añadir un `DOCS/UI_DESIGN_SYSTEM_FILES.md` (este archivo) y crear plantilla `CONTRIBUTING-UI.md` para guiar cómo añadir componentes al DS.

---

Si quieres, hago:
- Opción A: crear un branch con la extracción de `ChoiceButton` y su story + test (recomendado como primer PR).
- Opción B: generar la plantilla `CONTRIBUTING-UI.md` y ejemplos de `Button` storybook.

Dime cuál prefieres y lo hago (puedo empezar por A y luego B).
