# FastAPI Production Boilerplate

> **Clone it. Configure it. Ship it.**
> A battle-tested FastAPI starter with everything you'd add anyway.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/plasmacat420/fastapi-production-boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/plasmacat420/fastapi-production-boilerplate/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-GHCR-2496ED?logo=docker)](https://github.com/plasmacat420/fastapi-production-boilerplate/pkgs/container/fastapi-production-boilerplate)
[![Docs](https://img.shields.io/badge/Docs-GitHub%20Pages-blue)](https://plasmacat420.github.io/fastapi-production-boilerplate)

---

## Why this exists

Every backend project starts the same way: add JWT auth, wire up database migrations, set up RBAC, configure a job queue, add rate limiting, write the boilerplate tests. By the time you're done with infrastructure, you've spent two weeks before writing a single line of your actual product.

This repo is that infrastructure, done right. It reflects the patterns used in production at fast-moving startups — clean layered architecture, async everywhere, background workers that survive crashes, and a test suite that runs in CI without a real database. Fork it, change the app name, and start building what matters.

---

## Features

### Auth & Security
- JWT access tokens (30 min) + refresh tokens (7 days) via `python-jose`
- bcrypt password hashing via `passlib`
- Token blacklisting on logout (Redis-backed)
- OAuth2 compatible (`/auth/login` works with standard OAuth2 flows)

### Role-Based Access Control
- Three built-in roles: `user`, `moderator`, `admin`
- Declarative route guards: `Depends(require_role("admin"))`
- Easy to extend with custom roles

### Database
- Async SQLAlchemy 2.0 + `asyncpg` (zero blocking I/O)
- Alembic migrations — versioned, reversible, reproducible
- UUID primary keys on all tables
- `TimestampMixin` with `created_at` / `updated_at` on every model
- SQLite fallback for tests (no postgres required in CI)

### Background Jobs
- Celery with Redis as both broker and result backend
- Beat scheduler for periodic jobs (default: token cleanup every hour)
- Example tasks: `send_welcome_email`, `cleanup_expired_tokens`
- Task retry with exponential backoff

### Observability
- Structured JSON-style request logging with `loguru`
- `X-Request-ID` header on every response (correlate logs)
- `/health` — liveness probe (always fast)
- `/health/ready` — readiness probe (checks DB + Redis connectivity)
- Request duration tracked on every log line

### Developer Experience
- Full OpenAPI docs at `/docs` (Swagger UI) and `/redoc`
- One-command local dev: `docker compose up`
- `ruff` for linting and formatting
- `pytest` with async support — runs against SQLite in CI
- GitHub Actions: CI on every PR, Docker image to GHCR on merge, docs to Pages
- 90%+ test coverage target

---

## Quick Start

```bash
git clone https://github.com/plasmacat420/fastapi-production-boilerplate
cd fastapi-production-boilerplate
cp .env.example .env          # edit SECRET_KEY at minimum
docker compose up             # postgres + redis + api + worker all start
```

API live at **http://localhost:8000**
Docs at **http://localhost:8000/docs**

### First API calls

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"me@example.com","password":"mypassword123","full_name":"Jane Doe"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"me@example.com","password":"mypassword123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Access protected route
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN"

# Admin: list all users
curl http://localhost:8000/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Project Structure

```
fastapi-production-boilerplate/
├── .github/workflows/
│   ├── ci.yml               # Run tests + lint on every push/PR
│   ├── docker-publish.yml   # Build & push multi-arch image to GHCR
│   └── docs.yml             # Deploy MkDocs site to GitHub Pages
│
├── app/
│   ├── main.py              # FastAPI app factory — wires everything together
│   ├── config.py            # Pydantic-settings — all config via env vars
│   ├── database.py          # Async engine, session factory, get_db dependency
│   ├── dependencies.py      # get_current_user, require_role RBAC guards
│   ├── exceptions.py        # Typed exceptions + consistent JSON error handlers
│   │
│   ├── models/              # SQLAlchemy ORM models only
│   │   ├── base.py          # DeclarativeBase + TimestampMixin
│   │   └── user.py          # User model (UUID PK, email, role, is_active)
│   │
│   ├── schemas/             # Pydantic request/response shapes
│   │   ├── user.py          # UserCreate, UserUpdate, UserResponse
│   │   └── auth.py          # LoginRequest, TokenResponse, RefreshRequest
│   │
│   ├── routers/             # HTTP layer — thin, delegates to services
│   │   ├── auth.py          # /auth/register|login|refresh|logout|me
│   │   ├── users.py         # /users/me, /users, /users/{id}
│   │   └── health.py        # /health, /health/ready
│   │
│   ├── services/            # Business logic — no FastAPI imports
│   │   ├── auth.py          # JWT creation/verification, password hashing
│   │   └── user.py          # Async CRUD for users
│   │
│   ├── middleware/
│   │   ├── logging.py       # Structured request/response logging
│   │   └── rate_limit.py    # slowapi limiter (60 req/min per IP)
│   │
│   └── workers/
│       ├── celery_app.py    # Celery instance + beat schedule
│       └── tasks.py         # send_welcome_email, cleanup_expired_tokens
│
├── alembic/                 # Database migrations
│   └── versions/
│       └── 001_create_users_table.py
│
├── tests/
│   ├── conftest.py          # Fixtures: test client, DB, users, auth headers
│   ├── test_auth.py         # Auth flow end-to-end tests
│   ├── test_users.py        # User CRUD + RBAC tests
│   ├── test_health.py       # Health endpoint tests
│   └── test_rate_limit.py   # Rate limiting tests
│
├── docs/                    # MkDocs source → GitHub Pages
├── scripts/
│   ├── create_admin.py      # CLI: create first admin user
│   └── seed.py              # Seed DB with test users
│
├── Dockerfile               # Multi-stage production image
├── docker-compose.yml       # Full stack: api + worker + beat + postgres + redis
├── docker-compose.test.yml  # Test runner against SQLite
├── mkdocs.yml               # Docs site config
├── pyproject.toml           # Dependencies + tool config
├── alembic.ini
└── .env.example
```

---

## Tech Decisions

| Technology | Why chosen | Alternative considered |
|-----------|-----------|----------------------|
| FastAPI | Async, auto-OpenAPI, fastest Python framework | Flask (sync), Django (heavy) |
| SQLAlchemy 2.0 async | Non-blocking DB I/O, best ORM in Python | Tortoise ORM, SQLModel |
| asyncpg | Fastest PostgreSQL driver for Python | psycopg3 |
| Alembic | Tight SQLAlchemy integration, rock-solid | Django migrations |
| python-jose | Actively maintained, cryptography backend | PyJWT |
| passlib + bcrypt | Industry standard, timing-safe | argon2-cffi (overkill for most) |
| Celery + Redis | Battle-tested, retries, monitoring, beat | ARQ, RQ (less ecosystem) |
| slowapi | Integrates with FastAPI state, simple API | custom middleware |
| loguru | Zero-config structured logging | structlog (more setup) |
| ruff | 100x faster than flake8+isort, one tool | black + flake8 + isort |

---

## Running Tests

```bash
pip install -e ".[dev]"

# Run all tests
pytest -v --cov=app

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

Tests use SQLite (no postgres needed). CI runs in GitHub Actions on every push.

---

## Docs Site

Full documentation is deployed to GitHub Pages:
**https://plasmacat420.github.io/fastapi-production-boilerplate**

Built with MkDocs Material. To run locally:
```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

---

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, build on it.
