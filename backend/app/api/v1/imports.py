
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User
from app.services.import_service import (
    import_students,
    import_marks,
    import_attendance,
)


router = APIRouter(
    prefix="/imports",
    tags=["Academic Data Imports"],
)


def _process_import(
    importer,
    file: UploadFile,
    db: Session,
    current_user: User,
):
    """
    Process an uploaded academic data file.

    The import service manages its own transaction.
    """

    filename = file.filename or ""
    file_bytes = file.file.read()

    # Capture primitive values BEFORE ending the
    # authentication transaction. This prevents
    # SQLAlchemy from refreshing the expired User object.
    institution_id = current_user.institution_id
    uploaded_by = current_user.id

    # Authentication performed a SELECT query, which
    # automatically started a read-only transaction.
    if db.in_transaction():
        db.rollback()

    try:
        result = importer(
            db=db,
            institution_id=institution_id,
            uploaded_by=uploaded_by,
            filename=filename,
            file_bytes=file_bytes,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/students")
def upload_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload student records from CSV or Excel."""

    return _process_import(
        importer=import_students,
        file=file,
        db=db,
        current_user=current_user,
    )


@router.post("/marks")
def upload_marks(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload examination marks from CSV or Excel."""

    return _process_import(
        importer=import_marks,
        file=file,
        db=db,
        current_user=current_user,
    )


@router.post("/attendance")
def upload_attendance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload attendance records from CSV or Excel."""

    return _process_import(
        importer=import_attendance,
        file=file,
        db=db,
        current_user=current_user,
    )
