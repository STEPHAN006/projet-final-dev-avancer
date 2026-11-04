"""FastAPI LifeOS Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lifeos.core.database import init_db
from lifeos.backend.routers import (
    tasks, projects, calendar, study, habits,
    streaks, goals, focus, stats, settings
)

def create_app() -> FastAPI:
    init_db()

    app = FastAPI(
        title="LifeOS — Executive Sanctuary API",
        description="Local offline-first REST API engine for LifeOS personal productivity system.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(stats.router, prefix="/api")
    app.include_router(tasks.router, prefix="/api")
    app.include_router(projects.router, prefix="/api")
    app.include_router(calendar.router, prefix="/api")
    app.include_router(study.router, prefix="/api")
    app.include_router(habits.router, prefix="/api")
    app.include_router(streaks.router, prefix="/api")
    app.include_router(goals.router, prefix="/api")
    app.include_router(focus.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")

    @app.get("/")
    def root():
        return {
            "name": "LifeOS API",
            "status": "online",
            "mode": "offline-first local sanctuary",
            "docs": "/docs"
        }

    return app

app = create_app()
