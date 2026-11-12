from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database.connection import engine

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router

from app.api.v1.student_analytics import router as student_analytics_router

from app.api.v1.declining_performance import router as declining_performance_router

from app.api.v1.subject_analytics import router as subject_analytics_router

from app.api.v1.attendance_analytics import router as attendance_analytics_router

from app.api.v1.attendance_performance import (
    router as attendance_performance_router,
)

from app.api.v1.ml_predictions import router as ml_predictions_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="School Academic Intelligence Platform",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    subject_analytics_router,
    prefix="/api/v1",
)

app.include_router(
    student_analytics_router,
    prefix="/api/v1",
)

app.include_router(
    declining_performance_router,
    prefix="/api/v1"
)

app.include_router(
    attendance_analytics_router, 
    prefix="/api/v1"
)

app.include_router(
    attendance_performance_router, 
    prefix="/api/v1"
)

app.include_router(
    ml_predictions_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to School Intelligence API",
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
    }


@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database()")
            )
            database_name = result.scalar_one()

        return {
            "status": "connected",
            "database": database_name,
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )
    