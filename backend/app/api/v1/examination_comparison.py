
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User, AcademicPeriod, Examination, Classroom, Subject

from app.schemas.examination_comparison import (
    ExaminationComparisonResponse,
)

from app.services.examination_comparison_service import (
    get_examination_comparison,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Examination Comparison"],
)


@router.get(
    "/examinations/comparison",
    response_model=ExaminationComparisonResponse,
)
def examination_comparison(
    academic_period_id: int = Query(..., ge=1),
    class_id: int | None = Query(default=None, ge=1),
    subject_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

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

        if school_class.academic_period_id != academic_period_id:
            raise HTTPException(
                status_code=400,
                detail="Class does not belong to the selected academic period",
            )

    if subject_id is not None:
        subject = db.execute(
            select(Subject).where(
                Subject.id == subject_id,
                Subject.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if subject is None:
            raise HTTPException(
                status_code=404,
                detail="Subject not found",
            )

    result = get_examination_comparison(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        class_id=class_id,
        subject_id=subject_id,
    )

    if not result["examinations"]:
        raise HTTPException(
            status_code=404,
            detail="No examination performance records found for the selected filters",
        )

    return result
