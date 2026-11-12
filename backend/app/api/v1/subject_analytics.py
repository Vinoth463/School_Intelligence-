
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User, AcademicPeriod, Examination, Classroom
from app.schemas.subject_analytics import SubjectPerformanceResponse
from app.services.subject_analytics_service import get_subject_performance


router = APIRouter(
    prefix="/analytics",
    tags=["Academic Analytics"],
)


@router.get(
    "/subjects",
    response_model=list[SubjectPerformanceResponse],
)
def subject_performance(
    academic_period_id: int | None = Query(default=None, ge=1),
    examination_id: int | None = Query(default=None, ge=1),
    class_id: int | None = Query(default=None, ge=1),
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

    if examination_id is not None:
        examination = db.execute(
            select(Examination).where(
                Examination.id == examination_id,
                Examination.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if examination is None:
            raise HTTPException(
                status_code=404,
                detail="Examination not found",
            )

        if (
            academic_period_id is not None
            and examination.academic_period_id != academic_period_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Examination does not belong to the selected academic period",
            )

    if class_id is not None:
        school_class = db.execute(
            select(Classroom).where(
                Classroom.id == class_id,
                Classroom.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if school_class is None:
            raise HTTPException(
                status_code=404,
                detail="Class not found",
            )

        if (
            academic_period_id is not None
            and school_class.academic_period_id != academic_period_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Class does not belong to the selected academic period",
            )

    return get_subject_performance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        examination_id=examination_id,
        class_id=class_id,
    )
