from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database.connection import engine


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="School Academic Intelligence Platform",
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