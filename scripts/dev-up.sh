#!/usr/bin/env bash
set -euo pipefail

# Demo local canónica (HOY):
# - Postgres por docker compose (backend/docker-compose.yml)
# - Backend con uvicorn (FastAPI)
# - Frontend con Next.js dev
#
# Este script NO hace deploy, no toca UI.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="${ROOT_DIR}/.runtime"

SKIP_DB=0
SKIP_MIGRATE=0
SKIP_SEED=0

usage() {
	cat <<'EOF'
Usage: scripts/dev-up.sh [options]

Starts the local demo stack (DB + backend + frontend).

Options:
	--skip-db       Do not run `docker compose up -d` (assumes DB already running)
	--skip-migrate  Do not run `alembic upgrade head`
	--skip-seed     Do not run seed scripts
	-h, --help      Show this help
EOF
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		--skip-db)
			SKIP_DB=1
			shift
			;;
		--skip-migrate)
			SKIP_MIGRATE=1
			shift
			;;
		--skip-seed)
			SKIP_SEED=1
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "[dev-up] Unknown arg: $1" >&2
			usage >&2
			exit 2
			;;
	esac
done

wait_for_url() {
	local url="$1"
	local label="$2"
	local attempts="${3:-60}"
	local sleep_s="${4:-0.25}"

	for _ in $(seq 1 "$attempts"); do
		if curl -fsS --max-time 1 "$url" >/dev/null 2>&1; then
			echo "[dev-up] OK: ${label}"
			return 0
		fi
		sleep "$sleep_s"
	done

	echo "[dev-up] ERROR: ${label} no respondió a tiempo (${url})" >&2
	return 1
}

mkdir -p "${RUNTIME_DIR}"

echo "[dev-up] Root: ${ROOT_DIR}"

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
	PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
	PYTHON_BIN="python"
else
	echo "[dev-up] ERROR: No se encontró python3/python en PATH" >&2
	exit 1
fi

cd "${ROOT_DIR}/backend"
if [[ "$SKIP_DB" -eq 1 ]]; then
	echo "[dev-up] 1) DB: skip (--skip-db)"
else
	echo "[dev-up] 1) Levantando Postgres (docker compose)..."
	docker compose up -d
fi

if [[ ! -f .venv/bin/activate ]]; then
	echo "[dev-up] 1.1) Backend venv: creando .venv (${PYTHON_BIN} -m venv)..."
	"${PYTHON_BIN}" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

REQ_HASH_FILE=".venv/.requirements.sha256"
REQ_HASH=""
if command -v sha256sum >/dev/null 2>&1; then
	REQ_HASH="$(sha256sum requirements.txt | awk '{print $1}')"
	PREV_HASH="$(cat "${REQ_HASH_FILE}" 2>/dev/null || true)"
	if [[ "${REQ_HASH}" != "${PREV_HASH}" ]]; then
		echo "[dev-up] 1.2) Backend deps: instalando requirements (cambio detectado)..."
		python -m pip install -U pip >/dev/null
		pip install -r requirements.txt
		echo "${REQ_HASH}" > "${REQ_HASH_FILE}"
	fi
else
	# Fallback sin hashing: instalamos una vez por ausencia de stamp.
	if [[ ! -f "${REQ_HASH_FILE}" ]]; then
		echo "[dev-up] 1.2) Backend deps: instalando requirements (primera vez)..."
		python -m pip install -U pip >/dev/null
		pip install -r requirements.txt
		echo "installed" > "${REQ_HASH_FILE}"
	fi
fi
if [[ "$SKIP_MIGRATE" -eq 1 ]]; then
	echo "[dev-up] 2) Migraciones: skip (--skip-migrate)"
else
	echo "[dev-up] 2) Migraciones (alembic upgrade head)..."
	alembic upgrade head
fi

if [[ "$SKIP_SEED" -eq 1 ]]; then
	echo "[dev-up] 3) Seed: skip (--skip-seed)"
else
	echo "[dev-up] 3) Seed (idempotente): exam + preguntas + usuario demo..."
	python -m scripts.seed_paes
	python -m scripts.seed_questions
	python -m scripts.seed_user
fi

echo "[dev-up] 4) Backend (uvicorn) en background: 127.0.0.1:8000"
# Compat: limpiamos archivos antiguos si existen.
rm -f .uvicorn.pid .uvicorn.log
rm -f "${RUNTIME_DIR}/backend.uvicorn.pid" "${RUNTIME_DIR}/backend.uvicorn.log"
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > "${RUNTIME_DIR}/backend.uvicorn.log" 2>&1 &
echo $! > "${RUNTIME_DIR}/backend.uvicorn.pid"

# Espera activa: evita race conditions con smoke tests.
if ! wait_for_url "http://127.0.0.1:8000/api/v1/health/" "Backend health" 80 0.25; then
	echo "[dev-up] Backend log (tail):" >&2
	tail -n 120 "${RUNTIME_DIR}/backend.uvicorn.log" >&2 || true
	exit 1
fi

echo "[dev-up] 5) Frontend (next dev) en background: 127.0.0.1:3000"
cd "${ROOT_DIR}/tutor-paes-frontend"

if [[ ! -d node_modules ]]; then
	echo "[dev-up] 5.1) Frontend deps: node_modules no existe, ejecutando npm ci..."
	npm ci
fi

rm -f .next-dev.pid .next-dev.log
rm -f "${RUNTIME_DIR}/frontend.next-dev.pid" "${RUNTIME_DIR}/frontend.next-dev.log"
nohup env NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 npm run dev -- --port 3000 > "${RUNTIME_DIR}/frontend.next-dev.log" 2>&1 &
echo $! > "${RUNTIME_DIR}/frontend.next-dev.pid"

if ! wait_for_url "http://127.0.0.1:3000" "Frontend" 80 0.25; then
	echo "[dev-up] Frontend log (tail):" >&2
	tail -n 120 "${RUNTIME_DIR}/frontend.next-dev.log" >&2 || true
	exit 1
fi

echo "[dev-up] OK"
echo "- Frontend: http://127.0.0.1:3000"
echo "- Backend:  http://127.0.0.1:8000/docs"
echo "- Health:   http://127.0.0.1:8000/api/v1/health/"
echo "- Logs/PIDs: ${RUNTIME_DIR}/ (backend.uvicorn.* / frontend.next-dev.*)"
