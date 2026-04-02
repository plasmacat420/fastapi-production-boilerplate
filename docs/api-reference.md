# API Reference

Base URL: `http://localhost:8000`

Interactive docs: [`/docs`](http://localhost:8000/docs) (Swagger UI) | [`/redoc`](http://localhost:8000/redoc)

---

## Authentication

All protected routes require the `Authorization: Bearer <access_token>` header.

---

## Auth Endpoints

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/auth/register` | No | — | Register new user, returns token pair |
| POST | `/auth/login` | No | — | Login with email + password |
| POST | `/auth/refresh` | No | — | Exchange refresh token for new access token |
| POST | `/auth/logout` | Yes | any | Logout current user |
| GET | `/auth/me` | Yes | any | Get current user profile |

### POST /auth/register

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "mypassword123",
  "full_name": "John Doe"
}
```

**Response 201:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errors:** `409` email already registered | `422` validation error

---

### POST /auth/login

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "mypassword123"
}
```

**Response 200:** Same as register.

**Errors:** `401` invalid credentials | `403` account deactivated

---

### POST /auth/refresh

**Request body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response 200:** Same token pair shape.

**Errors:** `401` invalid or expired refresh token

---

## User Endpoints

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET | `/users/me` | Yes | any | Get own profile |
| PATCH | `/users/me` | Yes | any | Update own profile (full_name) |
| GET | `/users` | Yes | admin | List all users (paginated) |
| GET | `/users/{user_id}` | Yes | admin or self | Get user by ID |
| DELETE | `/users/{user_id}` | Yes | admin | Soft-delete user (sets is_active=false) |

### GET /users/me

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "last_login": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### PATCH /users/me

**Request body:**
```json
{
  "full_name": "Jane Doe"
}
```

### GET /users?skip=0&limit=20

**Query params:** `skip` (default 0), `limit` (default 20, max 100)

**Response 200:** Array of UserResponse objects.

---

## Health Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Liveness probe |
| GET | `/health/ready` | No | Readiness probe (checks DB + Redis) |

### GET /health

**Response 200:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /health/ready

**Response 200:**
```json
{
  "status": "ready",
  "db": "ok",
  "redis": "ok"
}
```

**Response 503** (if any dependency is down):
```json
{
  "status": "degraded",
  "db": "ok",
  "redis": "error: Connection refused"
}
```

---

## Error Format

All errors return consistent JSON:

```json
{
  "error": "NOT_FOUND",
  "message": "User not found",
  "status_code": 404
}
```

| Error Code | Status | Meaning |
|------------|--------|---------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient role / inactive account |
| `NOT_FOUND` | 404 | Resource does not exist |
| `CONFLICT` | 409 | Duplicate resource (e.g. email) |
| `ERROR` | 500 | Unexpected server error |
