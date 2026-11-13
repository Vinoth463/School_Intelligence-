
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User, Classroom, Subject
from app.schemas.period_comparison import PeriodComparisonResponse
from app.services.period_comparison_service import get_period_comparison


router = APIRouter(
    prefix="/analytics",
    tags=["Academic Period Comparison"],
)


@router.get(
    "/periods/comparison",
    response_model=PeriodComparisonResponse,
)
def period_comparison(
    class_id: int | None = Query(default=None, ge=1),
    subject_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    class_grade = None
    class_section = None

    # Validate the selected class and obtain its grade and section.
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

        class_grade = school_class.grade
        class_section = school_class.section

    # Validate the selected subject.
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

    result = get_period_comparison(
        db=db,
        institution_id=institution_id,
        class_grade=class_grade,
        class_section=class_section,
        class_id=class_id,
        subject_id=subject_id,
    )

    if not result["periods"]:
        raise HTTPException(
            status_code=404,
            detail="No academic performance records found for the selected filters",
        )

    return result
