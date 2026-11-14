
from decimal import Decimal
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.subject_analytics_service import (
    get_subject_performance,
)
from app.services.attendance_analytics_service import (
    get_low_attendance_students,
)
from app.ai.academic_support_service import (
    get_students_with_low_marks_and_attendance,
)
from app.services.declining_performance_service import (
    get_declining_performance,
)
from app.services.student_analytics_service import (
    get_student_performance,
)

from app.ml.feature_service import build_prediction_features
from app.ml.prediction_service import predict_underperformance

from app.models.student import Student
from app.models.subject import Subject
from app.models.examination import Examination


def make_json_safe(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            make_json_safe(item)
            for item in value
        ]

    return value


def retrieve_academic_data(
    db: Session,
    institution_id: int,
    question: str,
    academic_period_id: int | None = None,
    class_id: int | None = None,
    subject_id: int | None = None,
    student_id: int | None = None,
    target_examination_id: int | None = None,
) -> dict:

    normalized_question = question.lower().strip()

    # 1. General academic data-quality questions.
    # Handle these before prediction intent so a question about whether
    # incomplete data is sufficient does not get mistaken for a request
    # to run an individual prediction.

    data_quality_keywords = (
        "incomplete",
        "incomplete records",
        "missing data",
        "missing records",
        "data quality",
        "data sufficiency",
        "data sufficient",
        "sufficient data",
        "reliable prediction",
        "reliably predict",
        "records are missing",
        "records are incomplete",
        "what information is missing",
        "which information is missing",
        "data availability",
    )

    is_data_quality_question = any(
        keyword in normalized_question
        for keyword in data_quality_keywords
    )

    if is_data_quality_question and student_id is None:
        return {
            "intent": "academic_data_quality",
            "data_used": [],
            "records_found": 0,
            "academic_data": {
                "scope": "general_guidance",
                "student_identified": False,
                "student_specific_records_retrieved": False,
                "available_student_fields": [],
                "missing_student_fields": [
                    "student identity",
                    "examination marks",
                    "subject-wise attendance records",
                    "historical examination records",
                    "target examination",
                ],
                "prediction_generated": False,
                "prediction_reliability": "not_assessable",
                "limitations": [
                    "No specific student was identified in the question.",
                    "No student-specific academic records were retrieved.",
                    "The actual available and missing fields cannot be verified without a student record.",
                ],
            },
            "message": (
                "This is a general academic data-quality question. "
                "No specific student was identified, and no individual "
                "examination or attendance records were retrieved. "
                "Therefore, no student-specific marks, attendance percentages, "
                "or risk indicators are available for assessment. "
                "To evaluate a student's academic performance, examination "
                "marks, maximum marks, examination dates, and historical "
                "results are needed. To evaluate attendance, attendance "
                "sessions and present or absent records are needed. "
                "Without sufficient historical marks and attendance features, "
                "an individual underperformance prediction cannot be generated "
                "reliably. No prediction was generated."
            ),
                    }


    explicit_prediction_keywords = (
        "predict",
        "prediction",
        "forecast",
        "will underperform",
        "generate a prediction",
        "run a prediction",
        "model score",
        "random forest",
        "explain the prediction",
        "explain this prediction",
        "explain the model prediction",
        "underperformance prediction",
        "risk prediction",
        "risk score",
        "risk category",
        "flagged for academic support",
        "why was the student flagged",
        "why was this student flagged",
        "why was he flagged",
        "why was she flagged",
    )

    prediction_context_keywords = (
        "risk",
        "underperformance",
        "underperforming",
        "flagged",
        "academic support",
        "risk indicators",
        "positive indicators",
        "contributing factors",
        "teacher intervention",
        "teacher interventions",
        "intervention",
        "recommendation",
        "recommendations",
    )

    has_prediction_entities = (
        student_id is not None
        and subject_id is not None
        and target_examination_id is not None
    )

    has_prediction_context = any(
        keyword in normalized_question
        for keyword in prediction_context_keywords
    )

    is_explicit_prediction_question = any(
        keyword in normalized_question
        for keyword in explicit_prediction_keywords
    )

    is_prediction_question = (
        is_explicit_prediction_question
        or (has_prediction_entities and has_prediction_context)
    )

    if is_prediction_question:

        if not has_prediction_entities:
            return {
                "intent": "underperformance_prediction",
                "data_used": [],
                "records_found": 0,
                "academic_data": {},
                "message": (
                    "To explain or generate an individual examination "
                    "underperformance prediction, please specify the "
                    "student, subject and target examination."
                ),
            }

        student = db.scalar(
            select(Student).where(
                Student.id == student_id,
                Student.institution_id == institution_id,
            )
        )

        subject = db.scalar(
            select(Subject).where(
                Subject.id == subject_id,
                Subject.institution_id == institution_id,
            )
        )

        examination = db.scalar(
            select(Examination).where(
                Examination.id == target_examination_id,
                Examination.institution_id == institution_id,
            )
        )

        if (
            student is None
            or subject is None
            or examination is None
        ):
            return {
                "intent": "underperformance_prediction",
                "data_used": [],
                "records_found": 0,
                "academic_data": {},
                "message": (
                    "The requested student, subject or examination "
                    "could not be found for this institution."
                ),
            }

        # Validate the academic period.
        if (
            academic_period_id is not None
            and examination.academic_period_id != academic_period_id
        ):
            return {
                "intent": "underperformance_prediction",
                "data_used": [],
                "records_found": 0,
                "academic_data": {},
                "message": (
                    "The target examination does not belong "
                    "to the selected academic period."
                ),
            }

        try:
            # Build historical academic features.
            features = build_prediction_features(
                db=db,
                institution_id=institution_id,
                student_id=student_id,
                subject_id=subject_id,
                target_examination_id=target_examination_id,
            )

            # Use the existing trained Random Forest model.
            prediction = predict_underperformance(features)

        except ValueError as exc:
            return {
                "intent": "underperformance_prediction",
                "data_used": [],
                "records_found": 0,
                "academic_data": {},
                "message": str(exc),
            }

        prediction_data = {
            "student": {
                "student_id": student.id,
                "name": (
                    f"{student.first_name} "
                    f"{student.last_name}"
                ).strip(),
                "admission_number": student.admission_number,
            },
            "subject": {
                "subject_id": subject.id,
                "name": subject.name,
            },
            "target_examination": {
                "examination_id": examination.id,
                "name": examination.name,
                "exam_date": examination.exam_date,
            },
            "academic_period_id": examination.academic_period_id,
            "prediction": prediction,
            "features_used": features,
        }

        return {
            "intent": "underperformance_prediction",
            "data_used": [
                "historical student examination marks",
                "historical subject attendance records",
                "Random Forest underperformance prediction",
                "model risk indicators and data sufficiency checks",
            ],
            "records_found": 1,
            "academic_data": make_json_safe(prediction_data),
            "message": (
                "Random Forest examination underperformance "
                "prediction generated successfully."
            ),
        }

    # 3. Combined low marks and attendance.

    marks_keywords = (
        "low marks",
        "poor marks",
        "low score",
        "poor score",
        "below 40",
        "underperforming",
    )

    attendance_keywords = (
        "low attendance",
        "poor attendance",
        "attendance below",
        "attendance less",
        "attendance percentage",
    )

    has_low_marks = any(
        keyword in normalized_question
        for keyword in marks_keywords
    )

    has_low_attendance = any(
        keyword in normalized_question
        for keyword in attendance_keywords
    )

    if has_low_marks and has_low_attendance:

        records = get_students_with_low_marks_and_attendance(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
            class_id=class_id,
            subject_id=subject_id,
            marks_threshold=40.0,
            attendance_threshold=75.0,
        )

        if student_id is not None:
            records = [
                record
                for record in records
                if record["student_id"] == student_id
            ]

        return {
            "intent": "low_marks_and_attendance",
            "data_used": [
                "student subject marks analytics",
                "student subject attendance analytics",
            ],
            "records_found": len(records),
            "academic_data": make_json_safe(records),
            "thresholds": {
                "marks_below": 40.0,
                "attendance_below": 75.0,
            },
            "message": (
                "Students meeting both the low marks and low "
                "attendance conditions retrieved successfully."
                if records
                else (
                    "No students were found who meet both the "
                    "low marks and low attendance conditions."
                )
            ),
        }

    # 4. Student-specific academic performance.

    student_performance_keywords = (
        "academic performance",
        "student performance",
        "overall performance",
        "performance history",
        "performance report",
        "exam results",
        "examination results",
        "marks",
        "report card",
    )

    if (
        student_id is not None
        and any(
            keyword in normalized_question
            for keyword in student_performance_keywords
        )
    ):

        student_data = get_student_performance(
            db=db,
            institution_id=institution_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
        )

        if student_data is None:
            return {
                "intent": "student_performance",
                "data_used": [
                    "student examination performance analytics"
                ],
                "records_found": 0,
                "academic_data": [],
                "message": (
                    "No examination performance records were found "
                    "for this student in the selected academic period."
                ),
            }

        return {
            "intent": "student_performance",
            "data_used": [
                "student examination performance analytics",
                "subject-wise marks and percentages",
                "examination-wise performance trends",
            ],
            "records_found": len(student_data["examinations"]),
            "academic_data": make_json_safe(student_data),
            "message": (
                "Student academic performance retrieved successfully."
            ),
        }

    # 5. Declining performance.

    decline_keywords = (
        "declining performance",
        "declining academic performance",
        "decline in academic performance",
        "decline in performance",
        "performance decline",
        "declining marks",
        "marks decreased",
        "marks decreasing",
        "marks dropped",
        "performance dropped",
        "performance decreasing",
        "getting worse",
        "academic decline",
        "students declining",
        "declining across examinations",
        "declining across consecutive examinations",
        "decline across examinations",
        "decline across consecutive examinations",
    )

    if any(
        keyword in normalized_question
        for keyword in decline_keywords
    ):

        records = get_declining_performance(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
            class_id=class_id,
            decline_threshold=0.0,
        )

        if student_id is not None:
            records = [
                record
                for record in records
                if record["student_id"] == student_id
            ]

        return {
            "intent": "declining_performance",
            "data_used": [
                "student examination performance analytics",
                "consecutive examination comparison",
            ],
            "records_found": len(records),
            "academic_data": make_json_safe(records),
            "message": (
                "Students with declining performance "
                "between consecutive examinations retrieved."
                if records
                else (
                    "No declining performance records were "
                    "found for the selected filters."
                )
            ),
        }

    # 6. Subject performance.

    subject_keywords = (
        "subject",
        "subjects",
        "lowest average",
        "highest average",
        "best subject",
        "worst subject",
        "subject performance",
        "subject marks",
    )

    if any(
        keyword in normalized_question
        for keyword in subject_keywords
    ):

        records = get_subject_performance(
            db=db,
            institution_id=institution_id,
            academic_period_id=academic_period_id,
            class_id=class_id,
            examination_id=target_examination_id,
        )

        if subject_id is not None:
            records = [
                record
                for record in records
                if record["subject_id"] == subject_id
            ]

        if not records:
            return {
                "intent": "subject_performance",
                "data_used": ["subject performance analytics"],
                "records_found": 0,
                "academic_data": [],
                "message": (
                    "No subject performance records were found "
                    "for the selected filters."
                ),
            }

        lowest_subject = min(
            records,
            key=lambda record: record["average_percentage"],
        )

        return {
            "intent": "subject_performance",
            "data_used": ["subject performance analytics"],
            "records_found": len(records),
            "academic_data": make_json_safe(records),
            "lowest_performing_subject": make_json_safe(
                lowest_subject
            ),
            "message": (
                "Subject performance records retrieved successfully."
            ),
        }

    # 7. Low attendance.

    attendance_only_keywords = (
        "attendance",
        "absent",
        "absence",
        "low attendance",
        "attendance percentage",
    )

    if any(
        keyword in normalized_question
        for keyword in attendance_only_keywords
    ):

        records = get_low_attendance_students(
            db=db,
            institution_id=institution_id,
            threshold=75.0,
            academic_period_id=academic_period_id,
            class_id=class_id,
        )

        if student_id is not None:
            records = [
                record
                for record in records
                if record["student_id"] == student_id
            ]

        return {
            "intent": "low_attendance",
            "data_used": ["student attendance analytics"],
            "records_found": len(records),
            "academic_data": make_json_safe(records),
            "message": (
                "Students below the 75% attendance threshold retrieved."
                if records
                else (
                    "No students were found below the "
                    "75% attendance threshold."
                )
            ),
        }

    # 8. Unsupported question.

    return {
        "intent": "unsupported",
        "data_used": [],
        "records_found": 0,
        "academic_data": [],
        "message": (
            "This question is not supported yet. "
            "Currently supported topics are academic performance, "
            "combined low marks and attendance, subject performance, "
            "declining performance, ML predictions, attendance and academic data quality."
        ),
    }
