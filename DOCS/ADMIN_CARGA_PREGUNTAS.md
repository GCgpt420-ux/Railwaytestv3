# Admin: carga de preguntas (sin tocar código)

Objetivo: que una persona con rol admin pueda **subir preguntas** usando la API, con validación y reporte de errores.

Requisito: tener un token admin válido (ver login/demo y `seed_user.py`).

---

## 1) Opción recomendada (Swagger UI)

1. Abre la documentación interactiva:
   - `http://<backend-host>/docs`

2. Click en **Authorize** y pega:
   - `Bearer <TU_TOKEN>`

3. Usa estos endpoints (tag `questions`):

- `POST /api/v1/questions/` (una pregunta)
- `POST /api/v1/questions/bulk` (muchas preguntas; recomendado)
- `GET /api/v1/questions/recent` (ver últimas)

---

## 2) Carga masiva: `POST /api/v1/questions/bulk`

### 2.1 Payload

Campos importantes:
- `questions`: lista de preguntas (cada una igual a `QuestionCreateIn`)
- `dry_run`: `true` valida y **no escribe**
- `atomic`: `true` = o se crean todas o ninguna

Ejemplo (2 preguntas):

```json
{
  "dry_run": true,
  "atomic": false,
  "questions": [
    {
      "subject_code": "M1",
      "topic_code": "ALG",
      "prompt": "Si x=2, ¿cuánto vale 3x?",
      "reading_text": null,
      "explanation": "Multiplicar por 3.",
      "difficulty": 1,
      "choices": [
        {"label": "A", "text": "3"},
        {"label": "B", "text": "6"},
        {"label": "C", "text": "8"},
        {"label": "D", "text": "9"}
      ],
      "correct_choice": "B"
    },
    {
      "subject_code": "M1",
      "topic_code": "ALG",
      "prompt": "¿Cuál es el resultado de 10/2?",
      "reading_text": null,
      "explanation": "División directa.",
      "difficulty": 1,
      "choices": [
        {"label": "A", "text": "2"},
        {"label": "B", "text": "4"},
        {"label": "C", "text": "5"},
        {"label": "D", "text": "8"}
      ],
      "correct_choice": "C"
    }
  ]
}
```

### 2.2 Respuesta

- `created`: cuántas se crearían/crearon
- `skipped`: cuántas se rechazaron
- `errors[]`: lista de errores con `index` (posición en `questions`), `error`, `detail`

Errores típicos:
- `subject_not_found` / `topic_not_found`
- `invalid_choices` (labels duplicados)
- `invalid_correct_choice`

---

## 3) Flujo sugerido para terceros

1) Subir con `dry_run=true` hasta que `errors=[]`.
2) Subir con `dry_run=false` y `atomic=true` (para evitar cargas parciales).
3) Revisar `GET /api/v1/questions/recent?limit=20`.

---

## 4) Notas operativas

- Si aparece `exam_not_seeded`, falta inicializar el catálogo PAES (`seed_paes.py`).
- Mantén el límite de `questions` razonable (máx 200 por request en este MVP).
