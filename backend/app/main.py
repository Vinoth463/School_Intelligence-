from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database.connection import engine
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.student_analytics import router as student_analytics_router
from app.api.v1.subject_analytics import router as subject_analytics_router
from app.api.v1.declining_performance import router as declining_performance_router

from app.api.v1.attendance_analytics import router as attendance_analytics_router
from app.api.v1.attendance_performance import (
    router as attendance_performance_router,
)

from app.api.v1.class_analytics import router as class_analytics_router
from app.api.v1.examination_comparison import (
    router as examination_comparison_router,
)
from app.api.v1.period_comparison import (
    router as period_comparison_router,
)

from app.api.v1.ml_predictions import router as ml_predictions_router
from app.api.v1.imports import router as imports_router
from app.api.v1.reports import router as reports_router


from app.api.v1.ai_assistant import router as ai_assistant_router
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="School Academic Intelligence Platform",
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)

# Academic analytics
app.include_router(student_analytics_router, prefix=API_PREFIX)
app.include_router(subject_analytics_router, prefix=API_PREFIX)
app.include_router(declining_performance_router, prefix=API_PREFIX)

# Attendance analytics
app.include_router(attendance_analytics_router, prefix=API_PREFIX)
app.include_router(attendance_performance_router, prefix=API_PREFIX)

# Class and examination analytics
app.include_router(class_analytics_router, prefix=API_PREFIX)
app.include_router(examination_comparison_router, prefix=API_PREFIX)
app.include_router(period_comparison_router, prefix=API_PREFIX)

# Machine learning
app.include_router(ml_predictions_router, prefix=API_PREFIX)

# Data imports
app.include_router(imports_router, prefix=API_PREFIX)

# Generative AI Academic Assistant
app.include_router(ai_assistant_router, prefix=API_PREFIX)

# Academic Reports
app.include_router(reports_router, prefix=API_PREFIX)

@app.get("/")
def root():
    return {
        "message": "Welcome to School Intelligence API",
        "version": settings.APP_VERSION,
        "status": "running",
    }


# Application health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
    }


# Database health check
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
