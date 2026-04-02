# Quick Start

Get from zero to a running API in under 5 minutes.

---

## Prerequisites

- Docker and Docker Compose installed
- Git

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/plasmacat420/fastapi-production-boilerplate
cd fastapi-production-boilerplate
```

---

## Step 2 — Configure environment

```bash
cp .env.example .env
```

Open `.env` and at minimum change:

```bash
SECRET_KEY=your-random-256-bit-string-here
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Step 3 — Start everything

```bash
docker compose up
```

This starts:
- **postgres** — database on port 5432
- **redis** — cache/broker on port 6379
- **api** — FastAPI on port 8000 (runs migrations automatically)
- **worker** — Celery worker
- **beat** — Celery beat scheduler

---

## Step 4 — Verify it's running

```bash
curl http://localhost:8000/health
# {"status":"ok","version":"0.1.0","timestamp":"..."}
```

Open the interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Step 5 — Create your first admin user

```bash
python scripts/create_admin.py \
  --email admin@example.com \
  --password securepassword123 \
  --name "Admin User"
```

---

## Step 6 — Register and authenticate

```bash
# Register a new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"mypassword123","full_name":"John Doe"}'

# Returns:
# {"access_token":"eyJ...","refresh_token":"eyJ...","token_type":"bearer"}

# Store the access token
TOKEN="eyJ..."

# Get your profile
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"

# Refresh when access token expires
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<your_refresh_token>"}'
```

---

## Running tests locally

```bash
pip install -e ".[dev]"
pytest -v --cov=app
```

---

## Local development without Docker

```bash
# Start postgres and redis via Docker, run the API locally
docker compose up postgres redis -d

pip install -e ".[dev]"
uvicorn app.main:app --reload
```
