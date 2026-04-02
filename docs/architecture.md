# Architecture

## Request Flow

```
HTTP Request
     │
     ▼
┌─────────────────────────────┐
│      CORS Middleware         │  Allow/deny cross-origin requests
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    SlowAPI Rate Limiter      │  60 req/min per IP (Redis-backed)
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    Logging Middleware        │  Attach X-Request-ID, log method/path/status/duration
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│         Router               │  /auth  /users  /health
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│       Dependencies           │  get_db → AsyncSession
│                             │  get_current_user → JWT verify → User
│                             │  require_role("admin") → RBAC check
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│         Service Layer        │  Business logic, no HTTP concepts here
│  auth.py  │  user.py        │  Password hashing, JWT creation, CRUD
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│     SQLAlchemy ORM           │  Async queries via asyncpg
│     (User model)             │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│         PostgreSQL           │  Primary data store
└─────────────────────────────┘
```

---

## Folder Structure Explained

```
app/
├── main.py          # App factory — wires everything together
├── config.py        # Pydantic-settings — all config from env vars
├── database.py      # Async engine, session factory, get_db dependency
├── dependencies.py  # FastAPI dependencies: auth guards, RBAC
├── exceptions.py    # Typed exceptions + JSON error handlers
│
├── models/          # SQLAlchemy ORM models only
│   ├── base.py      # DeclarativeBase + TimestampMixin
│   └── user.py      # User model with UUID PK
│
├── schemas/         # Pydantic I/O schemas (request/response shapes)
│   ├── user.py      # UserCreate, UserUpdate, UserResponse
│   └── auth.py      # LoginRequest, TokenResponse, RefreshRequest
│
├── routers/         # HTTP layer — thin, delegates to services
│   ├── auth.py      # Register, login, refresh, logout
│   ├── users.py     # Profile CRUD, admin user management
│   └── health.py    # Liveness + readiness probes
│
├── services/        # Business logic — no FastAPI imports
│   ├── auth.py      # JWT, password hashing
│   └── user.py      # User CRUD operations
│
├── middleware/      # Starlette middleware
│   ├── logging.py   # Structured request logging
│   └── rate_limit.py # slowapi limiter instance
│
└── workers/         # Background tasks
    ├── celery_app.py # Celery + beat schedule
    └── tasks.py     # Task definitions
```

---

## Key Design Decisions

### Why async SQLAlchemy?
FastAPI is async-first. Using `asyncpg` + async SQLAlchemy means database I/O never blocks the event loop. Under load, this allows thousands of concurrent requests on a single process.

### Why separate schemas from models?
ORM models represent database structure. Pydantic schemas represent API contracts. Keeping them separate means you can evolve your database schema without breaking the API and vice versa.

### Why a service layer?
Routers handle HTTP (status codes, request parsing, response shaping). Services handle business logic (no `Request`, no `Response`). This makes services trivially testable without an HTTP client.

### Why Celery over FastAPI BackgroundTasks?
`BackgroundTasks` runs in the same process — if the API process dies, tasks are lost. Celery persists tasks in Redis and can retry on failure. For anything that touches external services (email, webhooks), you want Celery.

### Why UUIDs instead of integer IDs?
UUIDs are non-sequential and don't leak enumeration information. You can't guess `user_id=1001` to find the next user. They also work cleanly in distributed systems.
