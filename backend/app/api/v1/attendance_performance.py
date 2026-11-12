
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models import AcademicPeriod, Classroom
from app.models import User

from app.schemas.attendance_performance import (
    AttendancePerformanceAnalysisResponse,
)

from app.services.attendance_performance_service import (
    get_attendance_performance_analysis,
)


router = APIRouter(
    prefix="/analytics/attendance",
    tags=["Attendance-Performance Analysis"],
)


@router.get(
    "/performance-analysis",
    response_model=AttendancePerformanceAnalysisResponse,
)
def attendance_performance_analysis(
    academic_period_id: int | None = Query(default=None, ge=1),
    class_id: int | None = Query(default=None, ge=1),

    high_attendance_threshold: float = Query(default=85.0, ge=0, le=100),
    low_attendance_threshold: float = Query(default=75.0, ge=0, le=100),
    low_marks_threshold: float = Query(default=40.0, ge=0, le=100),
    high_marks_threshold: float = Query(default=75.0, ge=0, le=100),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    if academic_period_id is not None:
        period = db.execute(
            select(AcademicPeriod).where(
                AcademicPeriod.id == academic_period_id,
                AcademicPeriod.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if period is None:
            raise HTTPException(
                status_code=404,
                detail="Academic period not found",
            )

    if class_id is not None:
        classroom = db.execute(
            select(Classroom).where(
                Classroom.id == class_id,
                Classroom.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if classroom is None:
            raise HTTPException(
                status_code=404,
                detail="Class not found",
            )

        if (
            academic_period_id is not None
            and classroom.academic_period_id != academic_period_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Class does not belong to the selected academic period",
            )

    if high_attendance_threshold < low_attendance_threshold:
        raise HTTPException(
            status_code=400,
            detail="High attendance threshold must be greater than or equal to low attendance threshold",
        )

    if high_marks_threshold < low_marks_threshold:
        raise HTTPException(
            status_code=400,
            detail="High marks threshold must be greater than or equal to low marks threshold",
        )

    result = get_attendance_performance_analysis(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        class_id=class_id,
        high_attendance_threshold=high_attendance_threshold,
        low_attendance_threshold=low_attendance_threshold,
        low_marks_threshold=low_marks_threshold,
        high_marks_threshold=high_marks_threshold,
    )

    return {
        "institution_id": institution_id,
        "academic_period_id": academic_period_id,
        "class_id": class_id,
        "high_attendance_threshold": high_attendance_threshold,
        "low_attendance_threshold": low_attendance_threshold,
        "low_marks_threshold": low_marks_threshold,
        "high_marks_threshold": high_marks_threshold,
        **result,
    }
