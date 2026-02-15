# Informe de cambios — 2026-02-12

## Pendiente resuelto

- Se eliminó el warning de Next.js: **"Unsupported metadata themeColor"** moviendo `themeColor` desde `metadata` a `viewport`.
- Archivo: `tutor-paes-frontend/app/layout.tsx`.
- Verificación: `npm run build` queda sin warnings.

## Resumen ejecutivo (qué quedó)

El frontend quedó alineado con la arquitectura acordada:

- `src/core/ui/*`: UI atómica (Button/Input/Card/Badge/Spinner) + stories.
- `src/core/tokens/*`: tokens sincronizados desde Tailwind.
- `src/api/*` + `src/api/services/*`: cliente HTTP + servicios por dominio hacia FastAPI.
- `src/features/*`: vistas y lógica por dominio.
- Hooks:
  - `src/core/hooks/*`: guards globales (auth/admin).
  - `src/features/quiz/hooks/*`: hooks del dominio quiz (`useQuiz`).

## Cambios principales (alto nivel)

### 1) UI atómica consolidada

- Se removió UI legacy (`src/components/ui/*` y `src/design-system/primitives/*`).
- Se consolidó la UI en `src/core/ui/*`.

### 2) API layer consolidada

- Se removió API legacy (`src/lib/api/*` y `src/lib/api.ts`).
- Se consolidó la API en `src/api/*` y `src/api/services/*`.

### 3) Shared components

- Se removieron componentes legacy en `src/components/common/*`.
- Se consolidó en `src/components/shared/*`.

### 4) Hooks movidos a la nueva estructura

- Se eliminó `src/hooks/*`.
- Se movió auth/admin a `src/core/hooks/*`.
- Se movió quiz a `src/features/quiz/hooks/useQuiz.ts`.

### 5) Documentación

- Se agregó/actualizó `DOCS/PROJECT_TREE.md` para reflejar el tree actual.

## Estado actual en git (para cerrar)

- Hay una refactorización grande sin commitear (muchos deletes y adds por migración).
- Sugerencia de lectura rápida:
  - `git diff --stat`
  - `git diff --name-status`
  - `git status --porcelain=v1`

### Diffstat (resumen numérico)

- 63 archivos cambiados (148 inserciones / 2478 borrados), principalmente por eliminación de legacy + reubicación.

## Archivos clave tocados (para revisar)

- `tutor-paes-frontend/app/layout.tsx` (viewport/themeColor)
- `tutor-paes-frontend/src/core/hooks/useRequireAuth.ts`
- `tutor-paes-frontend/src/core/hooks/useRequireAdmin.ts`
- `tutor-paes-frontend/src/features/quiz/hooks/useQuiz.ts`
- `DOCS/PROJECT_TREE.md`

## Próximo paso sugerido

- Si quieres “cerrar” la migración: hacer stage + commit.
  - `git add -A`
  - `git commit -m "refactor(frontend): migrate to core/ui + api/services + hooks"`
