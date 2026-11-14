
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import (
    User,
    ImportLog,
    ImportRejection,
)

from app.schemas.imports import (
    ImportHistoryResponse,
    ImportHistoryItem,
    ImportRejectionListResponse,
    ImportRejectionResponse,
)

from app.services.import_service import (
    import_students,
    import_marks,
    import_attendance,
)


router = APIRouter(
    prefix="/imports",
    tags=["Academic Data Imports"],
)


# ============================================================
# 1. COMMON IMPORT PROCESSING
# ============================================================

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

    # Capture primitive values before ending the
    # authentication transaction.
    institution_id = current_user.institution_id
    uploaded_by = current_user.id

    # Authentication may have started a transaction.
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


# ============================================================
# 2. UPLOAD STUDENTS
# ============================================================

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


# ============================================================
# 3. UPLOAD MARKS
# ============================================================

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


# ============================================================
# 4. UPLOAD ATTENDANCE
# ============================================================

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


# ============================================================
# 5. IMPORT HISTORY
# ============================================================

@router.get(
    "/history",
    response_model=ImportHistoryResponse,
)
def get_import_history(
    import_type: str | None = Query(
        default=None,
        pattern="^(students|marks|attendance)$",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve import history for the authenticated institution.

    Optional filters:
    - import_type
    - limit
    - offset
    """

    institution_id = current_user.institution_id

    filters = [
        ImportLog.institution_id == institution_id,
    ]

    if import_type is not None:
        filters.append(
            ImportLog.import_type == import_type
        )

    total = db.scalar(
        select(func.count(ImportLog.id)).where(*filters)
    ) or 0

    imports = db.scalars(
        select(ImportLog)
        .where(*filters)
        .order_by(ImportLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return ImportHistoryResponse(
        total=total,
        items=[
            ImportHistoryItem.model_validate(item)
            for item in imports
        ],
    )


# ============================================================
# 6. IMPORT REJECTION DETAILS
# ============================================================

@router.get(
    "/{import_id}/rejections",
    response_model=ImportRejectionListResponse,
)
def get_import_rejections(
    import_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve rejected rows for a specific import.

    Only imports belonging to the authenticated
    institution can be accessed.
    """

    institution_id = current_user.institution_id

    # Verify that the import belongs to this institution.
    import_log = db.scalar(
        select(ImportLog).where(
            ImportLog.id == import_id,
            ImportLog.institution_id == institution_id,
        )
    )

    if import_log is None:
        raise HTTPException(
            status_code=404,
            detail="Import record not found.",
        )

    filters = [
        ImportRejection.import_log_id == import_id,
    ]

    total = db.scalar(
        select(func.count(ImportRejection.id)).where(*filters)
    ) or 0

    rejections = db.scalars(
        select(ImportRejection)
        .where(*filters)
        .order_by(ImportRejection.row_number.asc())
        .offset(offset)
        .limit(limit)
    ).all()

    return ImportRejectionListResponse(
        import_id=import_id,
        total=total,
        items=[
            ImportRejectionResponse.model_validate(item)
            for item in rejections
        ],
    )
