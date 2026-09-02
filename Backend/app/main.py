import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import DatabaseManager

from app.api import (
    users,
    workspaces,
    documents,
    dashboard,
    chat,
    reports,
    red_flags,
    extraction,
    comparisons,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await DatabaseManager.connect_db()

    yield

    # Shutdown
    await DatabaseManager.close_db()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Backend API for the Multi-Agent "
        "Financial Research System"
    ),
    lifespan=lifespan,
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# API ROUTERS
# =========================

app.include_router(
    users.router,
    prefix=settings.API_V1_STR
)

app.include_router(
    workspaces.router,
    prefix=settings.API_V1_STR
)

app.include_router(
    documents.router,
    prefix=settings.API_V1_STR
)

app.include_router(
    dashboard.router,
    prefix=settings.API_V1_STR
)

app.include_router(
    chat.router,
    prefix=settings.API_V1_STR
)

app.include_router(
    reports.router,
    prefix=settings.API_V1_STR
)

# Extraction Agent
app.include_router(
    extraction.router,
    prefix=settings.API_V1_STR
)

# Red Flag Agent
app.include_router(
    red_flags.router,
    prefix=settings.API_V1_STR
)

# Comparison Agent
app.include_router(
    comparisons.router,
    prefix=settings.API_V1_STR
)


# =========================
# HEALTH CHECK
# =========================

@app.get(
    "/health",
    tags=["System Status"]
)
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": (
            "mock_in_memory"
            if DatabaseManager.is_mock
            else "live_mongodb"
        ),
    }


# =========================
# ROOT ENDPOINT
# =========================

@app.get(
    "/",
    tags=["System Status"]
)
async def root():
    return {
        "message": (
            "Welcome to the Multi-Agent "
            "Financial Research System API"
        ),
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )