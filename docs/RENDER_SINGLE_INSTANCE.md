# Single-Instance Render Deployment Guide

This guide explains how to deploy Voice-Teller on Render's free tier using a single instance that runs the API, Redis, and Celery worker together.

## Overview

For Render's free tier, you can only create one web service. This setup consolidates:
- **FastAPI** (uvicorn) - on port 8000
- **Redis** - on port 6379 (internal to the container)
- **Celery worker** - manages async tasks
- **PostgreSQL** - external Render database

All processes are managed by `supervisord` inside one container.

## Architecture

```
┌─────────────────────────────────────────┐
│      Render Web Service (1 instance)    │
│  ┌──────────────────────────────────┐  │
│  │  supervisord (process manager)   │  │
│  ├──────────┬──────────┬────────────┤  │
│  │ API      │ Redis    │ Celery     │  │
│  │ :8000    │ :6379    │ worker     │  │
│  └──────────┴──────────┴────────────┘  │
└─────────────────────────────────────────┘
         ↓
┌──────────────────────────┐
│ Render PostgreSQL (free) │
│ External database        │
└──────────────────────────┘
```

## Render Setup Steps

### 1. Create PostgreSQL Database on Render

- Go to https://dashboard.render.com
- Click **New +** → **PostgreSQL**
- Name: `voice-teller-db`
- Region: Choose your preferred region
- PostgreSQL Version: 15 (or latest)
- Click **Create Database**
- Note the connection string (you'll need this)

### 2. Create Web Service on Render

- Click **New +** → **Web Service**
- **Repository**: Connect your GitHub repo
- **Name**: `voice-teller-api`
- **Runtime**: Docker
- **Build Command**: Leave default (or skip)
- **Start Command**: Leave empty (Dockerfile handles it)
- **Region**: Same as your database
- **Plan**: Free

### 3. Set Environment Variables in Render

Go to the Web Service settings and add these env vars:

```
DATABASE_URL=<your-render-postgres-connection-string>
REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

CORS_ORIGINS=https://your-netlify-site.netlify.app

GEMINI_API_KEY=<your-key>
ELEVENLABS_API_KEY=<your-key>

RESEND_API_KEY=<your-resend-api-key>
RESEND_FROM_EMAIL=Voice Teller <onboarding@resend.dev>

SECRET_KEY=<generate-a-random-key>

KEEPALIVE_ENABLE=true
KEEPALIVE_INTERVAL_SECONDS=300
KEEPALIVE_URL=https://your-render-service.onrender.com/health
```

### 4. Build & Deploy

- Render will auto-detect the `Dockerfile.render` or use `backend/Dockerfile`
- If you want to use `Dockerfile.render` specifically, update your service build settings to point to `backend/Dockerfile.render`
- Push to your repo's main branch, and Render will deploy automatically

### 5. Verify Deployment

```bash
curl https://your-render-service.onrender.com/health
```

Should return:
```json
{"status": "ok"}
```

## Files Used

- **`backend/Dockerfile.render`** - Production Dockerfile with supervisord
- **`backend/supervisord.conf`** - Process configuration (API, Redis, Celery)
- **`backend/core/config.py`** - Updated to use localhost for Redis/Celery by default

## Important Notes

### Redis Data Persistence

⚠️ **Redis data is ephemeral** on Render's free tier because:
- Render uses a read-only filesystem (except `/tmp`)
- If the service restarts, all Redis data is lost
- OTP codes stored in Redis will be cleared on restart

**Workarounds:**
- Use an external managed Redis (e.g., Redis Labs free tier with `redis.io` or `upstash.com`)
- Accept ephemeral OTP codes (users must verify quickly after request)
- Implement persistent OTP storage in PostgreSQL instead of Redis (alternative)

### Performance

- Free Render instances are shared and slower than paid tiers
- Expect longer startup times (0-2 minutes)
- The instance may spin down after 15 minutes of inactivity (but keep-alive pings help)

### Celery Worker

The Celery worker in `supervisord.conf` is optional. If you don't need async task processing, comment it out in the config and restart.

## Local Development (Docker Compose)

To keep your local development using Docker Compose, set these env vars:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/aivoice
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

Then run:
```bash
docker-compose up --build
```

## Troubleshooting

### "Redis connection refused"

- Verify Redis is running: check Render logs for `[program:redis]` output
- Ensure `REDIS_URL=redis://127.0.0.1:6379/0` is set

### "Database connection failed"

- Verify `DATABASE_URL` points to your Render PostgreSQL connection string
- Check the database exists and credentials are correct

### OTP codes expire immediately

- This happens when Redis restarts; switch to external managed Redis or accept ephemeral OTPs

### API crashes on startup

- Check logs in Render dashboard
- Ensure all required env vars are set
- Run `alembic upgrade head` migrations (add as startup script if needed)

## Next Steps

1. After deployment, add the Netlify frontend URL to `CORS_ORIGINS`
2. Set up a Render Cron Job for keep-alive pings (optional but recommended)
3. Monitor logs in Render dashboard during first deploy
