# Checklist demo (piloto privado)

## Objetivo
Piloto para jefes/profesores/alumnos/conocidos: validar flujo, claridad y UX. No es lanzamiento público.

## Acceso y fricción
- Un link único + instrucciones de 2-3 pasos.
- Presentar el login como "acceso de prueba" (evitar lenguaje que suene inseguro).

## Copy y confianza
- Nombrar como "Piloto" o "Versión de prueba".
- Explicar en 1 párrafo: qué hace, qué no hace, y qué feedback necesitas.
- Disclaimer: "No ingreses datos sensibles".

## Flujo mínimo impecable
- Landing → Login → Dashboard → Elegir tema → 5 preguntas → Resumen final → Volver al dashboard.
- Nunca pantalla en blanco: siempre loading o error recuperable.

## Manejo de errores
- Errores de red/timeout: mensaje humano + botón Reintentar + Volver al dashboard.
- Sesión expirada/401: volver a login con mensaje claro.

## Mobile (alumnos)
- Verificación en 360×800 y 390×844: alternativas cómodas, botones grandes, lectura sin fricción.

## Contenido demo coherente
- Preguntas representativas (no infantiles) + feedback entendible.
- No activar mocks/fallback silencioso en producción; si existe modo demo, que sea explícito.

## Instrumentación mínima
- Registrar 3 eventos: inicio quiz, respuesta enviada, tema completado (aunque sea logs).
- Link visible a formulario de feedback (Google Form/Typeform) o WhatsApp con plantilla.

## Qué pedir de feedback
- ¿Se entiende qué hacer?
- ¿Qué parte confundió?
- ¿Cómo se sintió el feedback?
- ¿En qué punto abandonarías?
