# 🔧 Arreglos para Railway - Actualización 15 Feb 2026

## Problemas Identificados

1. **PYTHONPATH no configurado**: Alembic no podía importar `app.db.base`
2. **Alembic no encontraba el módulo**: Error en `from app.db.base import Base`
3. **Sin variable de entorno PYTHONPATH**: El contenedor no sabía dónde buscar el paquete `app`

## ✅ Cambios Realizados

### 1. Dockerfile (`backend/Dockerfile`)
```dockerfile
# ANTES:
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app ..."]

# AHORA:
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app  # ← NUEVO
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn app.main:app ..."]
         ↑
    Asegura que Python encuentra alembic
```

### 2. Migrations `/backend/migrations/env.py`
```python
# ANTES: Solo load_dotenv() sin manejo de errores
# AHORA:
import sys
sys.path.insert(0, os.path.dirname(...))  # Garantiza que encuentra app/
try:
    load_dotenv()
except Exception:
    pass  # No falla si no hay .env (producción)
```

## 🚀 Cómo Proceder en Railway

### Opción 1: Retry el build (Recomendado)
1. Ve a https://railway.app
2. En el servicio de Railwaytestv3, haz click en `Deploy from GitHub`
3. Selecciona la rama `main`
4. Railway detectará los cambios y hará rebuild automático

### Opción 2: Forzar rebuild
1. En Railway, ve a `Settings` del servicio
2. Busca `Build & Deploy`
3. Haz click en `Force Train` o `Redeploy`

## ✅ Checklist para Railway

- [ ] Backend buildea sin errores "Error creating build plan"
- [ ] Dockerfile se ejecuta correctamente
- [ ] Alembic corre migraciones sin error
- [ ] Uvicorn inicia en puerto $PORT
- [ ] Health check responde: `GET /api/v1/health/`

## 📋 Variables de Entorno en Railway

Verifica que estén configuradas:
```
DATABASE_URL=postgresql+psycopg://localhost:5432/... (Railway autoproporciona)
SECRET_KEY=<generado con openssl rand -hex 32>
LOG_LEVEL=INFO
AUTO_CREATE_TABLES=false
CORS_ORIGINS=https://tutor-ia-paes-*.vercel.app
```

## 🧪 Prueba Local (opcional)

```bash
cd backend
docker build -t tutorpaes-backend:test .
docker logs <container-id>
```

Si el build falla localmente, Railway también fallará. Si pasa localmente, debería pasar en Railway.

## 📌 Resumen de Archivos Modificados

1. ✅ `/backend/Dockerfile` - PYTHONPATH y python -m alembic
2. ✅ `/backend/migrations/env.py` - Mejor manejo de imports y .env
3. ✅ `/railway.json` - Config en raíz
4. ✅ `/backend/railway.json` - Usa DOCKERFILE builder
5. ✅ `/backend/.env.example` - Variables de referencia
6. ✅ `/front-end/tutor-ia-paes/vercel.json` - Config de Vercel
7. ✅ `/front-end/tutor-ia-paes/.env.example` - Variables del frontend
