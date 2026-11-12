
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import AcademicPeriod, Classroom, Student, User

from app.services.attendance_analytics_service import (
    get_student_attendance,
    get_subject_attendance,
    get_class_attendance,
    get_low_attendance_students,
)

from app.schemas.attendance_analytics import (
    StudentAttendanceResponse,
    SubjectAttendanceResponse,
    ClassAttendanceResponse,
    LowAttendanceResponse,
)


router = APIRouter(
    prefix="/analytics/attendance",
    tags=["Attendance Analytics"],
)


def validate_academic_period(
    db: Session,
    institution_id: int,
    academic_period_id: int,
):
    period = db.query(AcademicPeriod).filter(
        AcademicPeriod.id == academic_period_id,
        AcademicPeriod.institution_id == institution_id,
    ).first()

    if period is None:
        raise HTTPException(
            status_code=404,
            detail="Academic period not found",
        )

    return period


def validate_class(
    db: Session,
    institution_id: int,
    class_id: int,
    academic_period_id: int | None = None,
):
    classroom = db.query(Classroom).filter(
        Classroom.id == class_id,
        Classroom.institution_id == institution_id,
    ).first()

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

    return classroom


@router.get(
    "/students",
    response_model=list[StudentAttendanceResponse],
)
def student_attendance(
    academic_period_id: int = Query(..., gt=0),
    class_id: int | None = Query(default=None, gt=0),
    student_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    validate_academic_period(
        db,
        institution_id,
        academic_period_id,
    )

    if class_id is not None:
        validate_class(
            db,
            institution_id,
            class_id,
            academic_period_id,
        )

    if student_id is not None:
        student = db.query(Student).filter(
            Student.id == student_id,
            Student.institution_id == institution_id,
        ).first()

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found",
            )

    return get_student_attendance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        class_id=class_id,
        student_id=student_id,
    )


@router.get(
    "/subjects",
    response_model=list[SubjectAttendanceResponse],
)
def subject_attendance(
    academic_period_id: int = Query(..., gt=0),
    class_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    validate_academic_period(
        db,
        institution_id,
        academic_period_id,
    )

    if class_id is not None:
        validate_class(
            db,
            institution_id,
            class_id,
            academic_period_id,
        )

    return get_subject_attendance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        class_id=class_id,
    )


@router.get(
    "/classes",
    response_model=list[ClassAttendanceResponse],
)
def class_attendance(
    academic_period_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    validate_academic_period(
        db,
        institution_id,
        academic_period_id,
    )

    return get_class_attendance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
    )


@router.get(
    "/low-attendance",
    response_model=list[LowAttendanceResponse],
)
def low_attendance_students(
    academic_period_id: int = Query(..., gt=0),
    threshold: float = Query(default=75.0, ge=0, le=100),
    class_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    validate_academic_period(
        db,
        institution_id,
        academic_period_id,
    )

    if class_id is not None:
        validate_class(
            db,
            institution_id,
            class_id,
            academic_period_id,
        )

    return get_low_attendance_students(
        db=db,
        institution_id=institution_id,
        threshold=threshold,
        academic_period_id=academic_period_id,
        class_id=class_id,
    )
