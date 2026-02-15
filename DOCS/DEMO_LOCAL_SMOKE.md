# Demo local robusta (smoke)

## Objetivo
Tener una validación mínima y repetible de que la demo local está bien:
- DB levantada
- Backend responde
- Frontend responde
- Login devuelve JWT
- Endpoints base del quiz responden

## Opción A (recomendado): script

```bash
./scripts/dev-up.sh
./scripts/smoke-demo.sh
```

Apagar:

```bash
./scripts/dev-down.sh
```

Logs/PIDs (runtime):
- `.runtime/backend.uvicorn.log` / `.runtime/backend.uvicorn.pid`
- `.runtime/frontend.next-dev.log` / `.runtime/frontend.next-dev.pid`

## Opción B: checklist manual (2–3 minutos)

1) Health

```bash
curl -sS http://127.0.0.1:8000/api/v1/health/
```

2) Login demo (token)

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com"}'
```

3) /auth/me con token

- Copia `access_token` y exporta:

```bash
export TOKEN='PEGA_AQUI'
curl -sS http://127.0.0.1:8000/api/v1/auth/me -H "Authorization: Bearer $TOKEN"
```

4) Next question (M1/ALG)

```bash
curl -sS "http://127.0.0.1:8000/api/v1/quiz/next-question?subject_code=M1&topic_code=ALG" \
  -H "Authorization: Bearer $TOKEN"
```

5) Frontend

Abrir http://127.0.0.1:3000

- Login con `demo@example.com`
- Dashboard carga materias
- Entrar a quiz (M1/ALG)
- Responder 1 pregunta y ver feedback

## Listo cuando
- No hay pantallas en blanco.
- Si hay falla de red/5xx, aparece CTA de reintento.
- Cambiar rápido de tópico no rompe el estado del quiz.
