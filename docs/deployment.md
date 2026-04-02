# Deployment

---

## Environment Variables Reference

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `APP_NAME` | `FastAPI Boilerplate` | No | App name shown in docs |
| `APP_VERSION` | `0.1.0` | No | Version string |
| `DEBUG` | `false` | No | Enable SQLAlchemy query logging |
| `DATABASE_URL` | — | **Yes** | Full async postgres URL |
| `SECRET_KEY` | — | **Yes** | 256-bit random string for JWT signing |
| `ALGORITHM` | `HS256` | No | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | No | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | No | Refresh token lifetime |
| `REDIS_URL` | `redis://localhost:6379/0` | **Yes** | Redis connection URL |
| `RATE_LIMIT_PER_MINUTE` | `60` | No | Requests per minute per IP |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | No | JSON array of allowed origins |

Generate a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Option 1: Docker Compose (Self-hosted VPS)

Best for: DigitalOcean, Hetzner, Linode, any Linux VPS.

```bash
# 1. Clone on your server
git clone https://github.com/plasmacat420/fastapi-production-boilerplate
cd fastapi-production-boilerplate

# 2. Configure environment
cp .env.example .env
nano .env   # set SECRET_KEY and DATABASE_URL

# 3. Start in detached mode
docker compose up -d

# 4. View logs
docker compose logs -f api

# 5. Run migrations (done automatically on startup)
# Or manually: docker compose exec api alembic upgrade head

# 6. Create first admin
docker compose exec api python scripts/create_admin.py \
  --email admin@yourdomain.com --password securepassword --name "Admin"
```

For HTTPS, put Nginx or Caddy in front:
```nginx
server {
    server_name api.yourdomain.com;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Option 2: Railway.app

Best for: Fastest path to production, automatic HTTPS, managed postgres + redis.

1. Fork this repo on GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Add services: **PostgreSQL** and **Redis** from the Railway marketplace
4. Set environment variables in the Railway dashboard:
   - `SECRET_KEY` — generate with `secrets.token_hex(32)`
   - `DATABASE_URL` — Railway auto-injects `${{Postgres.DATABASE_URL}}`
   - `REDIS_URL` — Railway auto-injects `${{Redis.REDIS_URL}}`
5. Set start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Railway detects Python automatically. Deploys on every push to `main`.

---

## Option 3: Render.com

Best for: Free tier with sleep, simple dashboard, managed databases.

1. Fork this repo
2. Go to [render.com](https://render.com) → New Web Service → Connect GitHub repo
3. Settings:
   - **Environment:** Python 3
   - **Build command:** `pip install -e .`
   - **Start command:** `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add PostgreSQL and Redis from Render's dashboard
5. Set environment variables (same as above)

Note: Free tier spins down after 15 minutes of inactivity. Use the `/health` endpoint as a keep-alive ping if needed.

---

## Production Checklist

- [ ] `SECRET_KEY` is a random 256-bit string (not the default)
- [ ] `DEBUG=false`
- [ ] Database is backed up (automated snapshots)
- [ ] HTTPS is enabled
- [ ] `CORS_ORIGINS` is restricted to your frontend domains
- [ ] Rate limiting is tuned for your traffic
- [ ] Celery worker is running (required for background tasks)
- [ ] `/health/ready` is wired to your load balancer health check
