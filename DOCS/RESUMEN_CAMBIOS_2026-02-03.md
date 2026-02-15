# Resumen de cambios (2026-02-03) — TutorPAES v2

Este documento resume los cambios aplicados recientemente en el proyecto (backend FastAPI + frontend Next.js), con foco en:

- Contrato del quiz (discriminante `kind`)
- Routing canónico del quiz (legacy `/quiz` → redirect estricto)
- Mocks: no ocultar errores cuando están OFF
- Seguridad: mitigación de IDOR (user_id derivado del JWT)
- Admin `/questions`: autorización real basada en DB (`is_admin`), no heurísticas

---

## 1) Cambios de contrato: `GET /api/v1/quiz/next-question`

### Qué se hizo
Se estandarizó la respuesta como unión discriminada por `kind`:

- `kind = "question"` cuando hay una pregunta para responder.
- `kind = "topic_completed"` cuando se agotó el tópico.

### Por qué
Evita heurísticas frágiles en frontend (por ejemplo “si vienen `score_*` entonces terminó”) y permite una discriminación explícita y estable.

### Archivos relevantes
- Backend schemas y endpoint de quiz (respuesta incluye `kind`).
- Frontend types y guards/mappers para discriminar por `kind`.

---

## 2) Routing canónico del Quiz (legacy vs canónico)

### Qué se hizo
- Ruta canónica: `/quiz/[subjectCode]`.
- Ruta legacy: `/quiz` ahora **solo** valida querystring y redirige; no inventa defaults.

### Reglas
- Si no hay `subjectCode` o es inválido → `notFound()`.
- Si es válido → redirect a `/quiz/[subjectCode]`.

### Por qué
Evita estados “mágicos” (p.ej. default `M1`, topic inventado, user_id hardcodeado) y centraliza la verdad sobre los subjects permitidos.

---

## 3) Mocks: no ocultar errores cuando están OFF

### Qué se hizo
Se corrigió el comportamiento de fallback en dashboard:

- Cuando `NEXT_PUBLIC_ENABLE_QUIZ_MOCKS !== "true"`:
  - Si la API falla, **se lanza error** (se ve en UI), no se reemplaza con mock silenciosamente.
- Cuando `NEXT_PUBLIC_ENABLE_QUIZ_MOCKS === "true"`:
  - Se permite fallback a mock para demo/dev.

### Por qué
En modo real, los errores deben ser visibles; si no, se enmascaran caídas de backend o errores de auth.

---

## 4) Seguridad: mitigación de IDOR (quiz + stats)

### Problema
Endpoints que aceptaban `user_id` por query/body permitían que un usuario enviara un `user_id` distinto al suyo y leyera/escribiera datos ajenos (IDOR).

### Qué se hizo
- Los endpoints relevantes ahora:
  - Requieren `Authorization: Bearer <token>`.
  - Derivan `user_id` desde el JWT (`sub`).
  - Si el cliente envía `user_id` y no coincide con el token → 403 con código de bloqueo.

### Por qué
El servidor debe ser el source of truth de identidad. El cliente no debe poder “elegir” su user_id.

---

## 5) Cierre robusto del attempt en `POST /quiz/answer`

### Problema que previene
Antes, el attempt podía quedar en `in_progress` indefinidamente si el usuario respondía la última pregunta y luego:

- cerraba la pestaña
- perdía conexión
- crasheaba el frontend

porque el cierre dependía de llamar nuevamente a `GET /quiz/next-question`.

### Qué se hizo
- `POST /api/v1/quiz/answer` ahora, después de guardar la respuesta, verifica si **quedan preguntas activas** sin responder para ese attempt.
- Si no quedan, marca el attempt como `completed` y devuelve `is_attempt_finished: true`.

### UX recomendado (mínimo cambio)
- Cuando `is_attempt_finished` es `true`, el frontend llama **una vez** a:

`GET /api/v1/quiz/next-question?subject_code=...&topic_code=...&attempt_id=<id>`

para obtener el payload final `kind: "topic_completed"` del attempt recién finalizado, sin iniciar un intento nuevo.

---

## 6) Admin `/questions`: gate real basado en DB (Checkpoint 6)

### Qué se cambió

#### 6.1 `User.is_admin` persistido
- Se agregó columna `is_admin` en `users` (boolean, default false, not null).
- Se agregó migración Alembic para crear la columna.

**Importante:** el admin ya NO se determina por `id==1` ni por email demo.

#### 6.2 Guard `require_admin_user`
- `require_admin_user` ahora permite acceso **solo si** `user.is_admin == True`.
- Esto es DB-backed porque `get_current_user`:
  - Decodifica JWT → extrae `sub`.
  - Hace query a DB por el user y retorna el modelo completo (incluye `is_admin`).

#### 6.3 Router `/questions` con dependencia global
Para evitar que se “olvide” el guard por endpoint, el router aplica:

- `dependencies=[Depends(require_admin_user)]`

Así, cualquier endpoint nuevo bajo `/questions` quedará protegido automáticamente.

#### 6.4 Seed idempotente de admin
El seed del demo user:
- Si no existe: lo crea con `is_admin=True`.
- Si existe: lo “upgradea” a `is_admin=True` y hace `commit`.

Esto es idempotente porque `email` es `unique`.

---

## 7) Pasos para aplicar en tu entorno

### 6.1 Migración
Desde `backend/`:

```bash
alembic upgrade head
```

### 6.2 Seed de admin demo
Desde la raíz del repo:

```bash
python3 -m backend.scripts.seed_user
```

---

## 8) Checklist de verificación (curl)

Asumiendo backend en `http://localhost:8000`.

### 7.1 Sin token → 401
```bash
curl -i http://localhost:8000/api/v1/questions/recent
```

### 7.2 Token normal (no admin) → 403
1) Login con un email cualquiera (no demo) para obtener token:
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user_normal@example.com","name":"Normal"}'
```

2) Usar el `access_token` en la llamada:
```bash
curl -i http://localhost:8000/api/v1/questions/recent \
  -H "Authorization: Bearer $TOKEN_NORMAL"
```

Debe responder 403 con código `ADMIN_REQUIRED`.

### 8.3 Token admin (demo) → 200
1) Login con el email demo (el configurado en `settings.DEMO_EMAIL`):
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","name":"Demo"}'
```

2) Llamar recent:
```bash
curl -i http://localhost:8000/api/v1/questions/recent \
  -H "Authorization: Bearer $TOKEN_ADMIN"
```

### 8.4 Crear pregunta (POST) — 401/403/200

Nota: para evitar errores por `subject_code/topic_code` inexistentes, conviene tomar un par real desde `recent` (o desde tus seeds).

1) Sin token → 401

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/questions/ \
  -H 'Content-Type: application/json' \
  -d '{
    "subject_code":"HIST",
    "topic_code":"GEO",
    "prompt":"[TEST] pregunta",
    "reading_text": null,
    "explanation":"Explicación",
    "difficulty": 1,
    "choices":[
      {"label":"A","text":"A"},
      {"label":"B","text":"B"},
      {"label":"C","text":"C"},
      {"label":"D","text":"D"}
    ],
    "correct_choice":"A"
  }'
```

2) Token normal → 403 (`ADMIN_REQUIRED`)

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/questions/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN_NORMAL" \
  -d '<MISMO_PAYLOAD>'
```

3) Token admin → 200

```bash
curl -i -X POST http://127.0.0.1:8000/api/v1/questions/ \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -d '<MISMO_PAYLOAD>'
```

---

## 9) Troubleshooting (problemas comunes)

### 9.1 `ModuleNotFoundError: No module named 'app'` al correr seeds
Pasa si ejecutas el script como archivo (ej: `python scripts/seed_user.py`) porque el `sys.path` queda apuntando a `backend/scripts/`.

Solución recomendada:

```bash
cd backend
python -m scripts.seed_user
```

Alternativa (no recomendada; preferir `python -m scripts.*`):

```bash
PYTHONPATH=. python scripts/seed_user.py
```

### 9.2 Health devuelve `307 Temporary Redirect`
El endpoint está en `/api/v1/health/` (con slash final). Si llamas `/api/v1/health` FastAPI redirige.

```bash
curl -i http://127.0.0.1:8000/api/v1/health/
```

### 9.3 Errores tipo “column users.is_admin does not exist”
La migración no se aplicó. Ejecuta:

```bash
cd backend
alembic upgrade head
```

### 9.4 `/questions/*` da 401 siempre
Verifica que estés enviando el header:

```bash
Authorization: Bearer <access_token>
```

Y que estés pegándole al host correcto (`127.0.0.1:8000` o el que uses).

### 9.5 `/questions/*` da 403 con token demo
Verifica que el demo user tenga `is_admin=true`:

```bash
cd backend
python -m scripts.seed_user
```

---

## 10) Notas y recomendaciones

- Preferir siempre DB-backed roles/permisos (como `is_admin`). Evitar roles en el token porque los tokens viejos podrían seguir siendo “admin” tras un cambio de rol.
- Mantener el guard en dependencia global para routers admin evita errores por omisión en endpoints nuevos.
- Mantener mocks estrictamente gated por env var y nunca enmascarar errores cuando la app está en modo real.

---

## 11) Archivos tocados (lista orientativa)

Backend:
- `backend/app/core/auth.py`
- `backend/app/db/models.py`
- `backend/app/api/v1/endpoints/questions.py`
- `backend/migrations/versions/b3a1f0c2d9e4_add_is_admin_to_users.py`
- `backend/scripts/seed_user.py`

Frontend (resumen de cambios históricos del mismo set de trabajo):
- Types/guards del quiz para `kind`
- APIs con `Authorization` y sin `user_id` manipulable
- Routing `/quiz` legacy solo redirect + validación
