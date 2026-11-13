
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import User, AcademicPeriod, Examination
from app.schemas.class_analytics import ClassPerformanceResponse
from app.services.class_analytics_service import get_class_performance


router = APIRouter(
    prefix="/analytics",
    tags=["Class Analytics"],
)


@router.get(
    "/classes/performance",
    response_model=list[ClassPerformanceResponse],
)
def class_performance(
    academic_period_id: int | None = Query(default=None, ge=1),
    examination_id: int | None = Query(default=None, ge=1),
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

        if academic_period_id is None:
            academic_period_id = examination.academic_period_id

    return get_class_performance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        examination_id=examination_id,
    )
