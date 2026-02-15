# Plan de mejora UI (Layout System) — TutorPAES MVP

Este documento guarda un set de **mejoras futuras** para que la UI “se sienta bien” sin rehacer lógica ni reescribir el Design System.

## Objetivo
Las pantallas se sienten inconsistentes principalmente por **layout** (ancho/padding/jerarquía/scroll), no por falta de estilos.

Lo que buscamos:
- Un **layout consistente** en todas las rutas.
- Que desktop no tenga “mar vacío” y mobile tenga buena lectura.
- Que el quiz maneje mejor textos largos (scroll controlado).

## Por qué calza con este repo
- El DS ya es la fuente de consistencia (primitives + wrappers + Storybook).
- Storybook debe seguir siendo liviano (sin depender de `globals.css`).
- `globals.css` debe ser sobrio: resets/fonts/base.

**Conclusión:** el siguiente paso lógico es una capa de **layout system** aplicada a páginas (contenedor + grid + spacing + tipografía).

---

## Paso 1 — PageContainer único (regla global)
**Qué:** definir y usar un contenedor estándar en todas las páginas internas.

**Regla recomendada (Tailwind):**
- `min-h-dvh`
- `max-w-6xl` (o `max-w-7xl` si necesitas más ancho)
- `mx-auto`
- `px-4 sm:px-6 lg:px-8`
- `py-6 sm:py-10`

**Resultado:** todo queda centrado y consistente, sin “anchos al azar”.

---

## Paso 2 — Landing responsiva (1 → 2 columnas)
**Qué:** Landing en grid.

**Regla:**
- Móvil: `grid-cols-1`
- Desktop: `lg:grid-cols-2`
- `gap-6 lg:gap-10`
- CTAs: `flex-col` en móvil → `sm:flex-row`

**Resultado:** en escritorio se ve “producto”; en móvil se lee natural.

---

## Paso 3 — Login responsivo (centrado real)
**Qué:** layout de login centrado + card con ancho correcto.

**Regla:**
- Wrapper: `min-h-dvh flex items-center justify-center`
- Card: `max-w-lg w-full`

**Resultado:** se siente moderno (tipo SaaS) y usable en móvil.

---

## Paso 4 — Dashboard responsivo (jerarquía + grid)
**Qué:** dividir en bloques y ordenar jerarquía.

**4.1 Bloque superior (progreso + continuar):**
- Desktop: grid 2 columnas
- Móvil: 1 columna

**4.2 Bloque materias/temas:**
- Móvil: 1 col
- `sm`: 2 col
- `lg`: 3 col

**Resultado:** dashboard se entiende rápido y se ve como panel.

---

## Paso 5 — Quiz responsivo (foco + lectura + scroll)
**Qué:** layout tipo “modo estudio”.

**Regla:**
- Móvil: 1 columna (texto arriba, opciones abajo)
- Desktop: 2 columnas (pasaje izquierda, pregunta+opciones derecha)
- Grid: `lg:grid-cols-[1.2fr_1fr]`

**Pasaje (lectura):**
- `max-h-[40dvh] lg:max-h-[70dvh] overflow-auto`

**Opciones:**
- padding táctil mínimo (ej. `py-3`)

**CTA:**
- Botón dentro del panel derecho, no una barra gigante suelta.

**Resultado:** experiencia real de estudio; texto largo no “rompe” el flujo.

---

## Principios de implementación (para no perder el efecto)
- No posicionamiento “a ojo” (evitar `absolute`/márgenes arbitrarios).
- Un solo contenedor por página (PageContainer).
- Una sola grilla por pantalla (no mezclar 3 layouts distintos).
- Jerarquía tipográfica consistente:
  - títulos escalan con `sm:` y `lg:`
  - cuerpo `text-sm sm:text-base`
- Interacción clara:
  - estados en choices (selected/correct/wrong/disabled)
  - loading states (Spinner DS)
  - disabled antes de seleccionar

---

## Checklist de aceptación (rápido)
- En desktop no hay “mar vacío” enorme.
- En móvil no hay overflow horizontal.
- Todo está centrado con el mismo padding.
- El quiz permite leer sin scroll infernal.
- Botones/opciones se tocan fácil (alto suficiente).
- El dashboard se entiende en 5 segundos.

---

## Nota
Estas mejoras se implementarán **después** del merge del PR grande del Design System, para no mezclar cambios estructurales con refinamientos visuales.
