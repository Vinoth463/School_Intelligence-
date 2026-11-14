
from sqlalchemy.orm import Session

from app.services.analytics_service import get_dashboard_overview
from app.services.student_analytics_service import get_student_performance
from app.services.subject_analytics_service import get_subject_performance
from app.services.class_analytics_service import get_class_performance

from app.services.attendance_analytics_service import (
    get_student_attendance,
    get_subject_attendance,
    get_class_attendance,
    get_low_attendance_students,
)


def get_overall_report(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
) -> dict:
    overview = get_dashboard_overview(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
    )

    subject_performance = get_subject_performance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
    )

    class_performance = get_class_performance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
    )

    class_attendance = get_class_attendance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
    )

    return {
        "overview": overview,
        "subject_performance": subject_performance,
        "class_performance": class_performance,
        "class_attendance": class_attendance,
    }


def get_student_report(
    db: Session,
    institution_id: int,
    student_id: int,
    academic_period_id: int | None = None,
) -> dict | None:
    performance = get_student_performance(
        db=db,
        institution_id=institution_id,
        student_id=student_id,
        academic_period_id=academic_period_id,
    )

    if performance is None:
        return None

    attendance = get_student_attendance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        student_id=student_id,
    )

    return {
        "student": performance,
        "attendance": attendance,
    }


def get_subject_report(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    examination_id: int | None = None,
    class_id: int | None = None,
) -> list[dict]:
    return get_subject_performance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        examination_id=examination_id,
        class_id=class_id,
    )


def get_class_report(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    examination_id: int | None = None,
) -> list[dict]:
    return get_class_performance(
        db=db,
        institution_id=institution_id,
        academic_period_id=academic_period_id,
        examination_id=examination_id,
    )


def get_attendance_report(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    class_id: int | None = None,
    threshold: float = 75.0,
) -> dict:
    return {
        "class_attendance": get_class_attendance(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
        ),
        "student_attendance": get_student_attendance(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
            class_id=class_id,
        ),
        "subject_attendance": get_subject_attendance(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
            class_id=class_id,
        ),
        "low_attendance_students": get_low_attendance_students(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
            class_id=class_id,
            threshold=threshold,
        ),
    }
