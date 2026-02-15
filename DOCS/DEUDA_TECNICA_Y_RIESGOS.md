# Deuda técnica y riesgos — TutorPAES v2 (MVP)

Este documento lista deuda y riesgos reales, con enfoque MVP: qué está “ok por ahora”, qué podría romperse, y qué mejorar después del deadline.

> Convención: cada ítem debe responder **qué**, **dónde**, **riesgo**, **mitigación MVP**, **post-deadline**.

---

## 1) Seguridad

### 1.1 Roles/Permisos
- Qué: autorización binaria (admin vs no admin).
- Dónde: `users.is_admin` (DB-backed).
- Riesgo: no hay RBAC granular (solo admin vs no admin).
- Mitigación MVP: aceptable.
- Post-deadline: definir roles/permisos por acción (p. ej. `manage_questions`, `view_stats`) y enforcement por endpoint.

### 1.2 JWT / Sesión
- Qué: token guardado en `localStorage`.
- Dónde: frontend (flujo de login).
- Riesgo: si el token queda en `localStorage`, existe exposición a XSS.
- Mitigación MVP: aceptable si la app controla contenido y evita HTML user-provided.
- Post-deadline: mover a cookies `HttpOnly` (y CSRF según flujo) y/o endurecer CSP.

---

## 2) Datos / migraciones

### 2.1 Migraciones redundantes/no-op
- Qué: hay migraciones vacías (`pass`) y un init duplicado.
- Riesgo: confusión operativa y onboarding lento.
- Acción: ver [DOCS/MIGRACIONES_Y_ESTADO_DB.md](MIGRACIONES_Y_ESTADO_DB.md).

### 2.2 `create_all` en startup
- Qué: `backend/app/main.py` ejecuta `Base.metadata.create_all(bind=engine)` en lifespan.
- Riesgo: en producción puede crear tablas “por fuera” de Alembic, desalineando el esquema.
- Mitigación MVP:
	- permitirlo solo en dev (idealmente controlado por flag), y documentar el valor recomendado por entorno.
	- en entornos no-dev: preferir correr migraciones siempre.
- Post-deadline:
	- deshabilitar `create_all` fuera de dev (flag/guard estricto).
	- exigir `alembic upgrade head` como paso obligatorio de deploy.

---

## 3) Quiz / consistencia

### 3.1 Contrato “topic_completed”
- Qué: contrato de respuesta discriminado por `kind`.
- Riesgo: front/back deben mantenerse sincronizados si crecen más `kind`.
- Mitigación MVP: mantener el contrato estable y documentado.
- Post-deadline: versionar `kind`/contratos o agregar tests contract.

### 3.2 Cierre robusto de Attempt
- Qué: el attempt se cierra en `POST /quiz/answer`.
- Riesgo: si se agregan “saltos” de pregunta o reintentos, la lógica de “quedan preguntas” debe revisarse.
- Mitigación MVP: no habilitar saltos/reintentos sin rediseñar el estado del attempt.

---

## 4) Frontend

### 4.1 Mocks
- Qué: mocks controlados por `NEXT_PUBLIC_ENABLE_QUIZ_MOCKS=true`.
- Riesgo: si el flag se activa por error en producción, se ocultan bugs.
- Mitigación MVP: documentar el flag y mantenerlo `false` por defecto.
- Post-deadline: bloquear mocks en `NODE_ENV=production` y/o en CI.

### 4.2 Manejo de errores
- Qué: estados de error/red en flujo de quiz/dashboard.
- Riesgo: si hay errores intermitentes de red, UX puede quedar en estados raros.
- Mitigación MVP: UI consistente de error con acción clara (reintentar/volver).
- Post-deadline: estrategia de retry/backoff + UI de reintento consistente.

---

## 5) Operación

### 5.1 Seeds idempotentes
- Qué: `seed_user.py` es idempotente (bien).
- Riesgo: otros seeds podrían no ser idempotentes o podrían duplicar data.
- Mitigación MVP: ejecutar seeds solo cuando sea necesario y en entornos controlados.
- Post-deadline: endurecer seeds con upserts o guards.

### 5.2 Observabilidad
- Qué: logging limitado para debugging productivo.
- Riesgo: diagnósticos lentos (sin request ID / sin contexto por request).
- Mitigación MVP: asegurar logs de error consistentes (endpoint + status + mensaje).
- Post-deadline: request IDs, structured logs, métricas básicas.

---

## 6) Checklist pre-release (MVP)
- [ ] `NEXT_PUBLIC_ENABLE_QUIZ_MOCKS=false`
- [ ] `AUTO_CREATE_TABLES=false` (si no es dev)
- [ ] `alembic upgrade head` ejecutado en entorno objetivo
- [ ] login → dashboard → quiz funcionan end-to-end con API real
