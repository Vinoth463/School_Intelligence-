
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User, Student, AcademicPeriod
from app.schemas.student_analytics import StudentPerformanceResponse
from app.services.student_analytics_service import get_student_performance


router = APIRouter(
    prefix="/analytics",
    tags=["Student Analytics"],
)


@router.get(
    "/students/{student_id}/performance",
    response_model=StudentPerformanceResponse,
)
def student_performance(
    student_id: int,
    academic_period_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    student = db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.institution_id == institution_id,
        )
    ).scalar_one_or_none()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

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

    result = get_student_performance(
        db=db,
        institution_id=institution_id,
        student_id=student_id,
        academic_period_id=academic_period_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Student performance records not found",
        )

    return result
