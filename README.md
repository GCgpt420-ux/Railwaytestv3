# 🎓 TutorPAES v2 - Sistema de Quiz Inteligente

Sistema de preparación para la Prueba de Acceso a la Educación Superior (PAES) de Chile, con feedback inteligente y tracking de progreso.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Testing](#testing)
- [Arquitectura](#arquitectura)
- [Documentación](#documentación)

## ✨ Características

 **Quiz Adaptativo**: Preguntas dinámicas por materia y tema PAES  
 **Feedback Inteligente**: Retroalimentación inmediata con explicaciones  
 **Dashboard Interactivo**: Visualización de progreso por materia/tema  
 **Idempotencia**: Respuestas duplicadas no corrompen datos  
 **Type Safety**: TypeScript + Pydantic para validación completa  
 **Logging**: Monitoreo de eventos críticos y debugging  
 **Configuración Centralizada**: Variables de entorno para todos los settings  

## 🛠️ Tecnologías

### Backend
- **FastAPI** 0.115+ - Framework web moderno
- **SQLAlchemy** 2.0 - ORM con type hints
- **PostgreSQL** 16 - Base de datos relacional
- **Pydantic** v2 - Validación de datos
- **Alembic** - Migraciones de DB

### Frontend
- **Next.js** 16 (App Router) - Framework React
- **TypeScript** 5 - Type safety
- **TailwindCSS** 4 - Styling
- **React** 19 - UI library

## 📦 Requisitos

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 16+
- **npm** o **yarn**

## 🚀 Instalación

## ✅ Demo local (canónica, reproducible)

> Objetivo: levantar **Postgres + Backend + Frontend** en un orden único y sin adivinar.

### Requisitos

- Docker (para Postgres)
- Python 3.11+
- Node.js 18+

### 1 comando (recomendado)

```bash
./scripts/dev-up.sh
```

Atajos útiles (más rápido para iterar):

```bash
# No baja/levanta Postgres si ya está corriendo
./scripts/dev-up.sh --skip-db

# No corre migraciones ni seed (solo levanta backend/frontend)
./scripts/dev-up.sh --skip-migrate --skip-seed
```

URLs:
- Frontend: http://127.0.0.1:3000
- Backend docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health/

Smoke test:

```bash
./scripts/smoke-demo.sh
```

Apagar todo:

```bash
./scripts/dev-down.sh
```

Si quieres apagar frontend/backend pero dejar Postgres arriba:

```bash
./scripts/dev-down.sh --keep-db
```

Logs/PIDs (runtime):
- `.runtime/backend.uvicorn.log` / `.runtime/backend.uvicorn.pid`
- `.runtime/frontend.next-dev.log` / `.runtime/frontend.next-dev.pid`

> Si prefieres hacerlo manual, ver DOCS/COMANDOS_DESARROLLO.md

### 1. Clonar Repositorio

```bash
git clone <repo-url>
cd ia_bot_v2
```

### 2. Backend Setup

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores (ver sección Configuración)

# Generar SECRET_KEY
openssl rand -hex 32  # Copiar resultado a .env

# Inicializar base de datos
alembic upgrade head

# Poblar datos iniciales
python -m scripts.seed_paes
python -m scripts.seed_questions
python -m scripts.seed_user

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd tutor-paes-frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus valores

# Iniciar servidor de desarrollo
npm run dev
```

### 4. Verificar Instalación

Backend: http://localhost:8000/docs (Swagger UI)
Frontend: http://localhost:3000

## ⚙️ Configuración

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/tutorpaes_db

# Security
SECRET_KEY=<resultado de openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_HOURS=24

# CORS (separado por comas)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Demo User
DEMO_EMAIL=demo@example.com

# Logging
LOG_LEVEL=INFO
DEBUG=False
```

### Frontend (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Demo Mode
# El login MVP no valida contraseña; basta con enviar email.
NEXT_PUBLIC_DEMO_EMAIL=demo@example.com
```

## Uso

1. Acceder a la Aplicación
http://localhost:3000

2. Login Demo
Email: demo@example.com
Password: (no se solicita en modo demo)

3. Flujo de Usuario
Login → Dashboard con materias disponibles
Seleccionar materia/tema → Iniciar quiz
Responder preguntas → Feedback inmediato
Completar tema → Ver score y estadísticas

## Testing

```bash
# 1. Login
# 2. Dashboard load
# 3. Iniciar quiz
# 4-6. Responder preguntas
# 7-8. Completar tema y validar score
# 9-10. Edge cases (idempotencia, validaciones)
# 11-12. Type guards y error handling
# 13-15. API endpoints directos
```

### Testing con curl (Endpoints)

```bash
# Stats
curl http://localhost:8000/api/v1/users/1/stats

# Next Question
curl "http://localhost:8000/api/v1/quiz/next-question?user_id=1&subject_code=M1&topic_code=ALG"

# Submit Answer
curl -X POST http://localhost:8000/api/v1/quiz/answer \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "subject_code": "M1",
    "topic_code": "ALG",
    "question_id": 1,
    "selected_choice_id": 1
  }'
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│ PostgreSQL  │
│  Frontend   │◀─────│   Backend    │◀─────│  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
   TypeScript          SQLAlchemy           Alembic
   TailwindCSS         Pydantic             Migrations

## Flujo de Datos

Usuario interactúa con componentes React
API Client (src/lib/api.ts) envía requests
FastAPI Endpoints procesan y validan
SQLAlchemy maneja queries a PostgreSQL
Pydantic Schemas validan respuestas
Frontend actualiza UI con datos

## Características Clave

Idempotencia: SNIPPET 2 en /quiz/answer
Type Safety: Union types discriminados (SNIPPET 3)
Validaciones: Edge cases críticos (SNIPPET 1)
Logging: Eventos auditables en producción

## 📚 Documentación

- [DOCS/CONTEXTO_GENERAL.md](DOCS/CONTEXTO_GENERAL.md)
- [DOCS/ARQUITECTURA.md](DOCS/ARQUITECTURA.md)
- [DOCS/MAPA_DEL_PROYECTO.md](DOCS/MAPA_DEL_PROYECTO.md)
- [DOCS/RESUMEN_CAMBIOS_2026-02-03.md](DOCS/RESUMEN_CAMBIOS_2026-02-03.md)
- [DOCS/MIGRACIONES_Y_ESTADO_DB.md](DOCS/MIGRACIONES_Y_ESTADO_DB.md)
- [DOCS/DEUDA_TECNICA_Y_RIESGOS.md](DOCS/DEUDA_TECNICA_Y_RIESGOS.md)
- [DOCS/ADMIN_CARGA_PREGUNTAS.md](DOCS/ADMIN_CARGA_PREGUNTAS.md)
- [DOCS/DEPLOY.md](DOCS/DEPLOY.md)
- [DOCS/COMANDOS_DESARROLLO.md](DOCS/COMANDOS_DESARROLLO.md)
- [DOCS/FRONTEND_CONVENCIONES.md](DOCS/FRONTEND_CONVENCIONES.md)
- [DOCS/PLAN_CORRECCION_FINAL.md](DOCS/PLAN_CORRECCION_FINAL.md)
