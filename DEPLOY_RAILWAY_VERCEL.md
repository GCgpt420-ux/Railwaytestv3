# Guía Rápida: Deploy en Railway + Vercel

## 1. Backend en Railway

### Cambios realizados:
✅ Configurado `railway.json` en raíz especificando contexto `backend/`
✅ Actualizado `Dockerfile` para ejecutar migraciones automáticamente
✅ Configurado CORS para Vercel

### Pasos en Railway:
1. Conecta el repo GitHub
2. Railway detectará el Dockerfile automáticamente
3. Agrega servicio PostgreSQL
4. Configura variables de entorno:
   ```
   DATABASE_URL=<Railway proporciona automáticamente>
   SECRET_KEY=<openssl rand -hex 32>
   CORS_ORIGINS=https://tutor-ia-paes-*.vercel.app
   LOG_LEVEL=INFO
   ```

### Health Check:
- Endpoint: `GET /api/v1/health/`
- Railway lo usa automáticamente

---

## 2. Frontend en Vercel

### Cambios realizados:
✅ Creado `vercel.json` en `front-end/tutor-ia-paes/`
✅ Creado `.env.example` con variables necesarias

### Pasos en Vercel:
1. Conecta el repo GitHub
2. **IMPORTANTE**: Root Directory = `front-end/tutor-ia-paes`
3. Configura variables de entorno:
   ```
   NEXT_PUBLIC_API_URL=https://<backend-railway-domain>
   NEXT_PUBLIC_DEMO_EMAIL=demo@example.com
   ```

---

## 3. Variables de Entorno

### Backend (.env en Railway):
```
DATABASE_URL=postgresql+psycopg://...
SECRET_KEY=xxx
CORS_ORIGINS=https://tutor-ia-paes-*.vercel.app
LOG_LEVEL=INFO
AUTO_CREATE_TABLES=false
```

### Frontend (.env.local en Vercel):
```
NEXT_PUBLIC_API_URL=https://<backend>.railway.app
NEXT_PUBLIC_DEMO_EMAIL=demo@example.com
```

---

## 4. Resolver Errores

**Railway "Error creating build plan"**
➜ Ya configurado con railway.json y Dockerfile

**Vercel no encuentra código**
➜ Verifica Root Directory = `front-end/tutor-ia-paes`

**CORS error en frontend**
➜ Actualiza CORS_ORIGINS en Railway

---

## 5. URLs Finales

Después del deploy:
- Backend: `https://railwaytestv3-<random>.railway.app`
- Frontend: `https://tutor-ia-paes-<branch>.vercel.app`
