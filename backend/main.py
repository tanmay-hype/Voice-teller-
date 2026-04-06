from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.router import api_router
from core.database import Base
from core.database import engine
import models


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
 try:
    print("debug tables", Base.metadata.tables.keys())
    # Create database tables on startup
    async with engine.begin() as conn:
        print("db connected")
        await conn.run_sync(Base.metadata.create_all)
        print("tables created")
 except Exception as e:
    print("Error during database setup:", e)