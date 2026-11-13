
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models import (
    User,
    Student,
    Subject,
    Examination,
    Classroom,
    AcademicPeriod,
    Mark,
)

from app.ml.feature_service import build_prediction_features
from app.ml.prediction_service import predict_underperformance

from app.schemas.ml_predictions import (
    UnderperformancePredictionRequest,
    UnderperformancePredictionResponse,
)


router = APIRouter(
    prefix="/ml",
    tags=["ML Predictions"],
)


# ============================================================
# 1. GET ACTIVE STUDENTS
# ============================================================

@router.get("/options/students")
def get_ml_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    students = db.execute(
        select(Student)
        .where(
            Student.institution_id == institution_id,
            Student.status == "active",
        )
        .order_by(Student.first_name, Student.last_name)
    ).scalars().all()

    return [
        {
            "id": student.id,
            "admission_number": student.admission_number,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "name": f"{student.first_name} {student.last_name}",
            "class_id": student.class_id,
        }
        for student in students
    ]


# ============================================================
# 2. GET AVAILABLE SUBJECTS
# ============================================================

@router.get("/options/subjects")
def get_ml_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    subjects = db.execute(
        select(Subject)
        .where(
            Subject.institution_id == institution_id,
        )
        .order_by(Subject.name)
    ).scalars().all()

    return [
        {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
        }
        for subject in subjects
    ]


# ============================================================
# 3. GET ELIGIBLE FUTURE EXAMINATIONS FOR A STUDENT
# ============================================================


@router.get("/options/examinations")
def get_ml_examinations(
    student_id: int = Query(..., ge=1),
    subject_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    # 1. Validate active student.
    student = db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.institution_id == institution_id,
            Student.status == "active",
        )
    ).scalar_one_or_none()

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active student not found in this institution.",
        )

    # 2. Validate subject.
    subject = db.execute(
        select(Subject).where(
            Subject.id == subject_id,
            Subject.institution_id == institution_id,
        )
    ).scalar_one_or_none()

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found in this institution.",
        )

    # 3. Validate the student's current class.
    school_class = db.execute(
        select(Classroom).where(
            Classroom.id == student.class_id,
            Classroom.institution_id == institution_id,
        )
    ).scalar_one_or_none()

    if school_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student class not found in this institution.",
        )

    # 4. Exclude examinations where this student
    #    already has marks for the selected subject.
    existing_marks = exists().where(
        Mark.student_id == student_id,
        Mark.subject_id == subject_id,
        Mark.examination_id == Examination.id,
    )

    # 5. Find eligible future examinations.
    examinations = db.execute(
        select(Examination)
        .join(
            AcademicPeriod,
            Examination.academic_period_id == AcademicPeriod.id,
        )
        .where(
            Examination.institution_id == institution_id,
            AcademicPeriod.institution_id == institution_id,

            Examination.academic_period_id
            == school_class.academic_period_id,

            Examination.exam_date > date.today(),

            Examination.exam_date >= AcademicPeriod.start_date,
            Examination.exam_date <= AcademicPeriod.end_date,

            ~existing_marks,
        )
        .order_by(Examination.exam_date)
    ).scalars().all()

    return [
        {
            "id": examination.id,
            "name": examination.name,
            "exam_date": examination.exam_date.isoformat(),
            "academic_period_id": examination.academic_period_id,
        }
        for examination in examinations
    ]



# ============================================================
# 4. EXISTING ML UNDERPERFORMANCE PREDICTION
# ============================================================

@router.post(
    "/predictions/underperformance",
    response_model=UnderperformancePredictionResponse,
    status_code=status.HTTP_200_OK,
)
def predict_student_underperformance(
    request: UnderperformancePredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    institution_id = current_user.institution_id

    try:
        # Build features using only this institution's records.
        features = build_prediction_features(
            db=db,
            institution_id=institution_id,
            student_id=request.student_id,
            subject_id=request.subject_id,
            target_examination_id=request.target_examination_id,
        )

        # Run the trained Random Forest model.
        prediction = predict_underperformance(features)

        return {
            "student_id": request.student_id,
            "subject_id": request.subject_id,
            "target_examination_id": request.target_examination_id,
            **prediction,
            "features": features,
        }

    except ValueError as exc:
        message = str(exc)

        if "not found" in message.lower():
            error_status = status.HTTP_404_NOT_FOUND
        elif "marks already exist" in message.lower():
            error_status = status.HTTP_409_CONFLICT
        else:
            error_status = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=error_status,
            detail=message,
        )
