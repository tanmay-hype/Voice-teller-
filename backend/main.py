from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.router import api_router
from core.database import Base
from core.database import engine
import models
from fastapi.staticfiles import StaticFiles

import asyncio
import logging
import os

import httpx


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json"
)

cors_origins = [origin.strip() for origin in getattr(settings, "CORS_ORIGINS", "").split(",") if origin.strip()]

if not cors_origins:
    cors_origins = ["https://ai-voice-teller.netlify.app"]

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Serve media files
import os
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/version")
def version_info():
    return {"project": settings.PROJECT_NAME, "version": settings.APP_VERSION}

@app.on_event("startup")
async def startup_event():
 try:
    print("debug tables", Base.metadata.tables.keys())
    # Create database tables on startup
    async with engine.begin() as conn:
        print("db connected")
        await conn.run_sync(Base.metadata.create_all)
        print("tables created")
    print(f"App version: {settings.APP_VERSION}")
 except Exception as e:
    print("Error during database setup:", e)
    # Start optional keep-alive background task to ping the app periodically
    try:
        if getattr(settings, "KEEPALIVE_ENABLE", False):
            interval = int(getattr(settings, "KEEPALIVE_INTERVAL_SECONDS", 300))
            keepalive_url = getattr(settings, "KEEPALIVE_URL", "http://127.0.0.1:8000/health")

            app.state._keepalive_running = True

            async def _keepalive_loop():
                logger = logging.getLogger("keepalive")
                logger.info("Keep-alive task started, pinging %s every %s seconds", keepalive_url, interval)
                async with httpx.AsyncClient(timeout=10.0) as client:
                    while app.state._keepalive_running:
                        try:
                            # best-effort GET
                            await client.get(keepalive_url)
                        except Exception as ex:
                            logger.debug("Keep-alive ping failed: %s", ex)
                        await asyncio.sleep(interval)

            # create background task and store the task handle
            app.state._keepalive_task = asyncio.create_task(_keepalive_loop())
    except Exception as ke:
        print("Error starting keepalive task:", ke)


@app.on_event("shutdown")
async def shutdown_event():
    # Cleanly stop the keep-alive task if running
    try:
        if getattr(app.state, "_keepalive_running", False):
            app.state._keepalive_running = False
        task = getattr(app.state, "_keepalive_task", None)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    except Exception as e:
        print("Error during shutdown keepalive cleanup:", e)