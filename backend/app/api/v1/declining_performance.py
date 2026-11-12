
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models import AcademicPeriod, Classroom, Student, User
from app.schemas.declining_performance import (
    DecliningPerformanceResponse,
    SubjectDeclineResponse,
)
from app.services.declining_performance_service import (
    get_declining_performance,
    get_subject_declines,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Declining Performance"],
)


@router.get(
    "/declining-performance",
    response_model=list[DecliningPerformanceResponse],
)
def read_declining_performance(
    academic_period_id: int | None = Query(default=None, gt=0),
    class_id: int | None = Query(default=None, gt=0),
    decline_threshold: float = Query(default=0.0, ge=0.0, le=100.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve students whose overall academic performance
    declined between consecutive examinations.
    """

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

    return get_declining_performance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        class_id=class_id,
        decline_threshold=decline_threshold,
    )


@router.get(
    "/declining-performance/subjects",
    response_model=list[SubjectDeclineResponse],
)
def read_subject_declines(
    academic_period_id: int = Query(..., gt=0),
    student_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve subject-wise performance declines between
    consecutive examinations within an academic period.

    Optionally filter the results for one student.
    """

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

    if student_id is not None:
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

    return get_subject_declines(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        student_id=student_id,
    )
