# FastAPI Production Boilerplate

> **Clone it. Configure it. Ship it.**
> A battle-tested FastAPI starter with everything you'd add anyway.

---

## What is this?

Every backend project ends up building the same foundation: authentication, role-based access control, database migrations, background jobs, rate limiting, structured logging, and CI/CD. This boilerplate ships all of it, production-ready, on day one.

Whether you're a startup launching your first product or an engineer bootstrapping an internal tool, this gives you a senior-level backend architecture you can fork and build on top of — without spending your first two weeks on infrastructure.

---

## Features

### Authentication & Security
- JWT access tokens + refresh tokens (python-jose)
- bcrypt password hashing (passlib)
- Token blacklisting on logout via Redis
- OAuth2 password flow compatible

### Role-Based Access Control
- Three built-in roles: `user`, `moderator`, `admin`
- Dependency-based route guards (`require_role("admin")`)
- Per-endpoint or per-router role enforcement

### Database
- Async SQLAlchemy 2.0 with `asyncpg`
- Alembic migrations (versioned, reversible)
- UUID primary keys, timestamp mixin
- SQLite fallback for testing (no postgres needed in CI)

### Background Jobs
- Celery + Redis broker
- Beat scheduler for periodic tasks
- Example tasks: `send_welcome_email`, `cleanup_expired_tokens`

### Observability
- Structured request logging with loguru
- X-Request-ID header on every response
- `/health` and `/health/ready` endpoints
- Duration tracking per request

### Developer Experience
- Full OpenAPI docs at `/docs` and `/redoc`
- Docker Compose for one-command local dev
- GitHub Actions: CI, Docker publish to GHCR, docs deploy to Pages
- ruff linting + formatting
- pytest with 90%+ coverage target

---

## Quick Start

```bash
git clone https://github.com/plasmacat420/fastapi-production-boilerplate
cd fastapi-production-boilerplate
cp .env.example .env          # edit SECRET_KEY at minimum
docker compose up             # postgres + redis + api + worker all start
```

API is live at [http://localhost:8000](http://localhost:8000)
Interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## First API call

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"me@example.com","password":"mypassword123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"me@example.com","password":"mypassword123"}'

# Access protected route
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

---

[Get Started →](quickstart.md){ .md-button .md-button--primary }
[View Architecture →](architecture.md){ .md-button }
