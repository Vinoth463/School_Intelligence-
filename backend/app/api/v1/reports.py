
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import (
    User,
    AcademicPeriod,
    Classroom,
    Examination,
    Student,
)
from app.services.reports_service import (
    get_overall_report,
    get_student_report,
    get_subject_report,
    get_class_report,
    get_attendance_report,
)

from app.services.reports_export_service import (
    generate_excel_report,
    generate_pdf_report,
)


router = APIRouter(
    prefix="/reports",
    tags=["Academic Reports"],
)


# --------------------------------------------------
# REPORT FILTER OPTIONS
# --------------------------------------------------

@router.get("/filter-options")
def get_report_filter_options(
    academic_period_id: int | None = Query(default=None, ge=1),
    class_id: int | None = Query(default=None, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    institution_id = current_user.institution_id

    # Academic periods
    periods = (
        db.query(AcademicPeriod)
        .filter(
            AcademicPeriod.institution_id == institution_id
        )
        .order_by(AcademicPeriod.start_date)
        .all()
    )

    # Classes
    class_query = db.query(Classroom).filter(
        Classroom.institution_id == institution_id
    )

    if academic_period_id is not None:
        class_query = class_query.filter(
            Classroom.academic_period_id == academic_period_id
        )

    classes = class_query.order_by(
        Classroom.grade,
        Classroom.section,
    ).all()

    # Examinations
    examination_query = db.query(Examination).filter(
        Examination.institution_id == institution_id
    )

    if academic_period_id is not None:
        examination_query = examination_query.filter(
            Examination.academic_period_id == academic_period_id
        )

    examinations = examination_query.order_by(
        Examination.exam_date
    ).all()

    # Students
    student_query = (
        db.query(Student)
        .join(
            Classroom,
            Student.class_id == Classroom.id,
        )
        .filter(
            Student.institution_id == institution_id,
            Classroom.institution_id == institution_id,
        )
    )

    if class_id is not None:
        student_query = student_query.filter(
            Student.class_id == class_id
        )

    if academic_period_id is not None:
        student_query = student_query.filter(
            Classroom.academic_period_id == academic_period_id
        )

    students = student_query.order_by(
        Student.first_name,
        Student.last_name,
    ).all()

    return {
        "academic_periods": [
            {
                "id": period.id,
                "name": period.name,
                "start_date": period.start_date,
                "end_date": period.end_date,
                "is_active": period.is_active,
            }
            for period in periods
        ],
        "classes": [
            {
                "id": classroom.id,
                "grade": classroom.grade,
                "section": classroom.section,
                "academic_period_id": classroom.academic_period_id,
                "label": (
                    f"{classroom.grade} - "
                    f"{classroom.section}"
                ),
            }
            for classroom in classes
        ],
        "examinations": [
            {
                "id": examination.id,
                "name": examination.name,
                "academic_period_id": examination.academic_period_id,
                "exam_date": examination.exam_date,
            }
            for examination in examinations
        ],
        "students": [
            {
                "id": student.id,
                "admission_number": student.admission_number,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "class_id": student.class_id,
                "label": (
                    f"{student.admission_number} - "
                    f"{student.first_name} "
                    f"{student.last_name}"
                ),
            }
            for student in students
        ],
    }

# --------------------------------------------------
# OVERALL ACADEMIC REPORT
# --------------------------------------------------

@router.get("/overview")
def overall_report(
    academic_period_id: int | None = Query(default=None, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_overall_report(
        db=db,
        institution_id=current_user.institution_id,
        academic_period_id=academic_period_id,
    )


# --------------------------------------------------
# STUDENT REPORT
# --------------------------------------------------

@router.get("/students/{student_id}")
def student_report(
    student_id: int,
    academic_period_id: int | None = Query(default=None, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = get_student_report(
        db=db,
        institution_id=current_user.institution_id,
        student_id=student_id,
        academic_period_id=academic_period_id,
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found in this institution.",
        )

    return report


# --------------------------------------------------
# SUBJECT REPORT
# --------------------------------------------------

@router.get("/subjects")
def subject_report(
    academic_period_id: int | None = Query(default=None, ge=1),
    examination_id: int | None = Query(default=None, ge=1),
    class_id: int | None = Query(default=None, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_subject_report(
        db=db,
        institution_id=current_user.institution_id,
        academic_period_id=academic_period_id,
        examination_id=examination_id,
        class_id=class_id,
    )


# --------------------------------------------------
# CLASS REPORT
# --------------------------------------------------

@router.get("/classes")
def class_report(
    academic_period_id: int | None = Query(default=None, ge=1),
    examination_id: int | None = Query(default=None, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_class_report(
        db=db,
        institution_id=current_user.institution_id,
        academic_period_id=academic_period_id,
        examination_id=examination_id,
    )


# --------------------------------------------------
# ATTENDANCE REPORT
# --------------------------------------------------

@router.get("/attendance")
def attendance_report(
    academic_period_id: int | None = Query(default=None, ge=1),
    class_id: int | None = Query(default=None, ge=1),
    threshold: float = Query(default=75.0, ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_attendance_report(
        db=db,
        institution_id=current_user.institution_id,
        academic_period_id=academic_period_id,
        class_id=class_id,
        threshold=threshold,
    )


# --------------------------------------------------
# REPORT DATA SELECTOR FOR EXPORTS
# --------------------------------------------------

def _get_export_data(
    report_type: str,
    db: Session,
    institution_id: int,
    academic_period_id: int | None,
    student_id: int | None,
    examination_id: int | None,
    class_id: int | None,
    threshold: float,
) -> dict:

    if report_type == "overview":
        return get_overall_report(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
        )

    if report_type == "student":
        if student_id is None:
            raise HTTPException(
                status_code=400,
                detail="student_id is required for a student report.",
            )

        report = get_student_report(
            db=db,
            institution_id=institution_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
        )

        if report is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found in this institution.",
            )

        return report

    if report_type == "subjects":
        return {
            "subject_performance": get_subject_report(
                db=db,
                institution_id=institution_id,
                academic_period_id=academic_period_id,
                examination_id=examination_id,
                class_id=class_id,
            )
        }

    if report_type == "classes":
        return {
            "class_performance": get_class_report(
                db=db,
                institution_id=institution_id,
                academic_period_id=academic_period_id,
                examination_id=examination_id,
            )
        }

    if report_type == "attendance":
        return get_attendance_report(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
            class_id=class_id,
            threshold=threshold,
        )

    raise HTTPException(
        status_code=400,
        detail="Invalid report_type. Use overview, student, subjects, classes, or attendance.",
    )


# --------------------------------------------------
# EXCEL EXPORT
# --------------------------------------------------

@router.get("/export/excel")
def export_excel(
    report_type: Literal[
        "overview",
        "student",
        "subjects",
        "classes",
        "attendance",
    ] = Query(default="overview"),
    academic_period_id: int | None = Query(default=None, ge=1),
    student_id: int | None = Query(default=None, ge=1),
    examination_id: int | None = Query(default=None, ge=1),
    class_id: int | None = Query(default=None, ge=1),
    threshold: float = Query(default=75.0, ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report_data = _get_export_data(
        report_type=report_type,
        db=db,
        institution_id=current_user.institution_id,
        academic_period_id=academic_period_id,
        student_id=student_id,
        examination_id=examination_id,
        class_id=class_id,
        threshold=threshold,
    )

    output = generate_excel_report(
        report_data=report_data,
        report_title=f"{report_type.title()} Academic Report",
    )

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                f'attachment; filename="{report_type}_report.xlsx"'
        },
    )


# --------------------------------------------------
# PDF EXPORT
# --------------------------------------------------

@router.get("/export/pdf")
def export_pdf(
    report_type: Literal[
        "overview",
        "student",
        "subjects",
        "classes",
        "attendance",
    ] = Query(default="overview"),
    academic_period_id: int | None = Query(default=None, ge=1),
    student_id: int | None = Query(default=None, ge=1),
    examination_id: int | None = Query(default=None, ge=1),
    class_id: int | None = Query(default=None, ge=1),
    threshold: float = Query(default=75.0, ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report_data = _get_export_data(
        report_type=report_type,
        db=db,
        institution_id=current_user.institution_id,
        academic_period_id=academic_period_id,
        student_id=student_id,
        examination_id=examination_id,
        class_id=class_id,
        threshold=threshold,
    )

    output = generate_pdf_report(
        report_data=report_data,
        report_title=f"{report_type.title()} Academic Report",
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{report_type}_report.pdf"'
        },
    )
