# Migraciones y estado de DB — TutorPAES v2

Objetivo: entender qué migraciones existen, cuáles son redundantes/sospechosas, cuál es el `head` actual y qué conviene (o no) limpiar antes del deadline.

Regla para deadline: **no borrar ni re-escribir migraciones ya aplicadas**. Lo seguro es documentar y dejar limpieza post-entrega.

---

## 1) Cómo está configurado Alembic

- Config: `backend/alembic.ini`
  - `script_location = backend/migrations`
  - `prepend_sys_path = .` (permite importar `app.*` en migraciones)

- Runtime env: `backend/migrations/env.py`
  - Usa `settings.DATABASE_URL` como URL real
  - `target_metadata = Base.metadata`

---

## 2) Árbol actual de migraciones (versions/)

Carpeta: `backend/migrations/versions/`

Archivos:

- `7140ca6c3d65_init_schema.py` (down_revision = None)
- `787db5040a31_init_schema.py` (down_revision = 7140..., pero tiene `pass`)
- `dd63e36c7aa1_add_exam_tables.py` (down_revision = 787d...)
- `1fe2ecfae783_attempt_completion_fields.py` (down_revision = dd63..., pero tiene `pass`)
- `70130b097505_add_reading_text_to_questions.py` (down_revision = 1fe2...)
- `b3a1f0c2d9e4_add_is_admin_to_users.py` (down_revision = 70130...)

Conclusión práctica: el `head` lógico es `b3a1f0c2d9e4`.

---

## 3) Hallazgos (redundancias / deuda)

### 3.1 “init schema” duplicado
- Hay dos archivos llamados “init schema”:
  - `7140...` crea tabla `users` muy básica (id, email)
  - `787d...` no agrega nada (upgrade/downgrade con `pass`)

Esto es **redundante**. No rompe por sí solo, pero agrega ruido.

### 3.2 Migraciones vacías (pass)
- `787db...` (pass)
- `1fe2ec...` (pass)

Esto es deuda: dificulta razonar del historial. Para el deadline, lo mejor es **documentarlo** y no tocarlo.

---

## 4) Recomendación para el deadline

### 4.1 Qué NO hacer antes de entregar
- No reordenar ni eliminar migraciones existentes.
- No “squashear” migraciones si ya hay DBs inicializadas en el equipo.

### 4.2 Qué SÍ hacer
- Dejar documentado:
  - cuál es el `head`
  - cuáles migraciones son no-op
  - cómo inicializar en un entorno limpio

### 4.3 Limpieza post-deadline (plan)
Si después del deadline quieres reducir ruido:

- Crear una migración base (squash) y reiniciar historial (solo si puedes resetear DBs del equipo).
- O mantener historial, pero:
  - agregar un `README` en `migrations/` explicando el porqué de las no-op
  - o reemplazar las no-op por migraciones reales (solo si no se aplicaron aún).

---

## 5) Comandos útiles

- Ver current head aplicado:

```bash
cd backend
alembic current
alembic heads
alembic history --verbose
```

- Inicialización en DB limpia:

```bash
cd backend
alembic upgrade head
python -m scripts.seed_paes
python -m scripts.seed_questions
python -m scripts.seed_user
```
