# Plan de corrección final (A/B/C/D)

Este documento formaliza el plan “por letras” y el estado actual del proyecto.

## Contexto

- Proyecto: **TutorPAES v2** (FastAPI + Next.js App Router)
- API base: `/api/v1`
- Frontend: convención **thin pages** (`app/**/page.tsx` delega en `src/features/**/views/*`)

## Estado del plan

### A — Imágenes fallando (pendiente)

**Estado:** Pendiente (no diagnosticado en runtime todavía).

**Síntomas esperados (ejemplos):**
- Imágenes no cargan (404), se quedan en blanco o aparecen rotas.
- Errores en consola relacionados a `next/image`, CSP, dominios remotos, rutas `public/`, etc.

**Checklist de diagnóstico (orden recomendado):**
1. DevTools → Network: filtrar por `Img` y revisar status (404/403/500), URL final, cache.
2. DevTools → Console: errores de `next/image`, CORS/CSP, mixed content.
3. Verificar si la imagen viene de:
   - `public/` (ruta debe ser absoluta desde `/`, ej: `/logo.png`)
   - dominio remoto (requiere permitirlo en `next.config.ts` con `images.remotePatterns`)
   - backend (validar `Content-Type`, CORS y ruta real)
4. Revisar si se está usando `next/image` correctamente (width/height, `unoptimized`, etc.).

**Criterio de aceptación:**
- Todas las imágenes del flujo principal (landing/login/dashboard/quiz) cargan sin errores en consola y sin requests fallidos.

### B — Error 422 en envío de respuesta (hecho)

**Estado:** Hecho.

**Qué se corrigió (resumen):**
- El frontend envía `selected_choice_id` como **ID numérico real** (DB), no como letra (A/B/C/D).
- Se mejoró el manejo de errores para mostrar feedback claro y permitir reintento.

**Criterio de aceptación:**
- `POST /api/v1/quiz/answer` responde 200/201 consistentemente con payload válido, sin 422 por tipo/formato de `selected_choice_id`.

### C — Admin: crear preguntas (parcial)

**Estado:** Parcial.

**Qué existe:**
- Backend: endpoints admin protegidos por JWT (crear/listar recientes).
- Frontend: ruta `/admin/questions` montada con la convención de views.

**Pendiente:**
- Validación end-to-end desde navegador:
  - Login → obtener token → crear pregunta → verificar que aparece en “recent”.
- Pulido de UX (mensajes, loading, manejo de errores, validaciones de formulario).

**Criterio de aceptación:**
- Un usuario admin puede crear una pregunta desde la UI y verla reflejada en el backend sin pasos manuales (excepto login).

### D — JWT / Seguridad (parcial)

**Estado:** Parcial (MVP funcional).

**Qué existe:**
- JWT emitido en login y verificación en endpoints admin.

**Pendiente (hardening):**
- Roles/claims reales (no “demo admin” por shortcut).
- Mejoras de expiración/refresh (si aplica) y manejo de sesión.
- Guardias de rutas más estrictas en frontend (si aplica).

**Criterio de aceptación:**
- Endpoints admin inaccesibles sin token válido y con autorización acorde al rol.

## Próximos pasos recomendados

1. Resolver **A** primero (impacta percepción inmediata del producto).
2. Cerrar **C** con prueba E2E en UI.
3. Endurecer **D** (roles/claims/guards) cuando C esté estable.
