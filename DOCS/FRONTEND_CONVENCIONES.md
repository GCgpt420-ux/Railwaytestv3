````markdown
# Convenciones Frontend (TutorPAES)

Este documento define las reglas prácticas que estamos usando para mantener el frontend consistente, fácil de navegar y escalable.

## Objetivo

- Mantener rutas (`app/**`) delgadas y predecibles.
- Agrupar UI y lógica por feature en `src/features/**`.
- Separar “pantallas” (views) de “piezas reutilizables” (components).
- Reducir importaciones frágiles y rutas largas.

## Estructura de carpetas

Ubicación principal del frontend:

- `tutor-paes-frontend/app/` (Next.js App Router)
- `tutor-paes-frontend/src/features/` (feature-first)

Convención dentro de un feature:

- `src/features/<feature>/views/`
  - Pantallas / flujos completos
  - Puede contener navegación, Suspense, lectura de query params, guards, etc.
- `src/features/<feature>/components/`
  - Componentes UI reutilizables dentro del feature (no orquestan navegación)
- `src/features/<feature>/hooks/`
  - Hooks del feature
- `src/features/<feature>/mappers/`
  - Transformaciones/adapters (si aplica)

Ejemplo:

- `src/features/quiz/views/QuizFlowView.tsx`
- `src/features/quiz/components/QuestionDisplay.tsx`

## “Páginas delgadas” (App Router)

Regla:

- Cada archivo `app/**/page.tsx` debe ser lo más delgado posible.
- Idealmente:
  - Lee `params` / `searchParams` (si es Server Component).
  - Renderiza una `*View` o `*PageView`.
  - No contiene UI compleja, ni lógica de negocio.

Motivación:

- Mejora mantenibilidad: las rutas son “entradas” claras.
- Evita mezclar responsabilidades (routing vs UI).
- Facilita testear y reusar pantallas.

## Nomenclatura: `*View` vs `*PageView`

- `*View`:
  - Pantalla principal (presentación + lógica propia de la pantalla).
  - Ej: `DashboardView`, `QuizFlowView`.

- `*PageView`:
  - Vista de nivel ruta que normalmente incluye:
    - Guard (ej. leer `localStorage` y redirigir)
    - `Suspense` + `useSearchParams`
    - Orquestación para elegir la pantalla
  - Ej: `DashboardPageView`.

Regla rápida:

- Si el archivo “se siente como la ruta”, probablemente sea `*PageView`.
- Si el archivo “se siente como la pantalla”, probablemente sea `*View`.

## Barrel exports (`index.ts`)

En `views/` usamos barrels para importaciones estables:

- `src/features/<feature>/views/index.ts`
  - Exporta las vistas públicas del feature.
  - Permite importaciones tipo: `import { QuizFlowView } from "@/features/quiz/views"`.

En `components/` solo usamos barrel si existen varios componentes compartidos reales.

- ✅ Úsalo si simplifica importaciones repetidas.
- ❌ Evitar archivos `index.ts` vacíos o “placeholders”.

## Imports recomendados

- Desde rutas (`app/**/page.tsx`):
  - Preferir barrels de `views/`.

Ejemplo:

```ts
import { QuizFlowView } from "@/features/quiz/views";
```

- Dentro de un mismo feature:
  - Preferir importaciones relativas para evitar ciclos raros vía barrels.

Ejemplos:

```ts
import { SubjectCard } from "../components";
import { DashboardView } from "./DashboardView";
```

## Hidratación (Next.js) y `localStorage`

Regla:

- Si el componente puede renderizar en server (Server Components o HTML pre-renderizado), evita leer `localStorage` en el primer render si eso cambia el HTML.
- En Client Components (`"use client"`) es aceptable leer `localStorage` en el initializer de `useState` si el render inicial resultante es consistente (y no causa mismatch).

Patrón recomendado:

- Render inicial estable (mismo HTML server/cliente).
- Leer `localStorage` en `useEffect` y actualizar estado.

Motivación:

- Evita warnings de `hydration mismatch`.

## Checklist rápido para PRs

- ¿Los `app/**/page.tsx` son delgados?
- ¿Las pantallas viven en `src/features/**/views/`?
- ¿Los componentes reutilizables viven en `components/`?
- ¿Los barrels (`index.ts`) existen solo donde aportan?
- ¿No se lee `localStorage` en el primer render (initializer) si produce mismatch?
- ¿`npm run build` pasa?

## Ejemplos reales en el repo

- Ruta delgada (server) → redirect (si falta `topicCode`):
  - `app/quiz/[subjectCode]/page.tsx` valida params/query y redirige a `/dashboard`.

- Ruta delgada (server) → Vista:
  - `app/quiz/[subjectCode]/page.tsx` → `src/features/quiz/views/QuizFlowView.tsx`

- Orquestador en `views/`:
  - `src/features/quiz/views/QuizFlowView.tsx`

- Componentes del feature + barrel:
  - `src/features/quiz/components/index.ts`


````
