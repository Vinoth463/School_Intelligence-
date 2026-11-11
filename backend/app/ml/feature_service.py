
from datetime import timedelta
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.marks import Mark
from app.models.attendance import Attendance
from app.models.examination import Examination
from app.models.classroom import Classroom


def _attendance_percentage(records):
    """
    Calculate attendance percentage.

    Present = 1
    Absent = 0
    """

    if not records:
        return 0.0

    present_count = sum(
        1 for record in records
        if record.status == "present"
    )

    return (present_count / len(records)) * 100.0


def build_prediction_features(
    db: Session,
    institution_id: int,
    student_id: int,
    subject_id: int,
    target_examination_id: int,
) -> dict:
    """
    Build the exact historical feature structure used
    during ML model training.

    Only information available up to the previous
    examination is used.

    The target examination's marks are never included.
    """

    # --------------------------------------------------
    # 1. VALIDATE STUDENT
    # --------------------------------------------------

    student = db.scalar(
        select(Student).where(
            Student.id == student_id,
            Student.institution_id == institution_id,
        )
    )

    if student is None:
        raise ValueError(
            "Student not found in this institution."
        )

    # --------------------------------------------------
    # 2. VALIDATE TARGET EXAMINATION
    # --------------------------------------------------

    target_exam = db.scalar(
        select(Examination).where(
            Examination.id == target_examination_id,
            Examination.institution_id == institution_id,
        )
    )

    if target_exam is None:
        raise ValueError(
            "Target examination not found in this institution."
        )

    # Do not generate predictions if the target marks
    # have already been recorded.
    existing_target_mark = db.scalar(
        select(Mark.id).where(
            Mark.student_id == student_id,
            Mark.subject_id == subject_id,
            Mark.examination_id == target_examination_id,
        )
    )

    if existing_target_mark is not None:
        raise ValueError(
            "Marks already exist for the target examination."
        )

    # --------------------------------------------------
    # 3. FETCH HISTORICAL EXAMINATION MARKS
    # --------------------------------------------------

    historical_rows = db.execute(
        select(Mark, Examination, Classroom)
        .join(
            Examination,
            Mark.examination_id == Examination.id,
        )
        .join(
            Classroom,
            Mark.class_id == Classroom.id,
        )
        .where(
            Mark.student_id == student_id,
            Mark.subject_id == subject_id,
            Examination.institution_id == institution_id,
            Classroom.institution_id == institution_id,
            Examination.exam_date < target_exam.exam_date,
        )
        .order_by(
            Examination.exam_date.asc(),
            Examination.id.asc(),
            Mark.id.asc(),
        )
    ).all()

    if not historical_rows:
        raise ValueError(
            "Insufficient historical examination marks "
            "to generate a prediction."
        )

    # --------------------------------------------------
    # 4. CALCULATE HISTORICAL MARK FEATURES
    # --------------------------------------------------

    previous_scores = []

    for mark, examination, classroom in historical_rows:

        percentage = (
            float(mark.obtained_marks)
            / float(mark.max_marks)
        ) * 100.0

        previous_scores.append(percentage)

    # Most recent examination percentage.
    previous_exam_percentage = previous_scores[-1]

    # Average of all examinations available so far.
    historical_average_percentage = mean(previous_scores)

    # Difference between latest and previous scores.
    # No trend is available when only one exam exists.
    if len(previous_scores) >= 2:
        marks_trend = (
            previous_scores[-1] - previous_scores[-2]
        )
    else:
        marks_trend = None

    previous_exam_count = len(previous_scores)

    # Use the historical class associated with
    # the student's latest examination mark.
    latest_mark, current_exam, current_class = historical_rows[-1]

    class_grade = current_class.grade

    # --------------------------------------------------
    # 5. FETCH ATTENDANCE UP TO CURRENT EXAMINATION
    # --------------------------------------------------

    cutoff_date = current_exam.exam_date

    attendance_records = db.scalars(
        select(Attendance)
        .where(
            Attendance.student_id == student_id,
            Attendance.subject_id == subject_id,
            Attendance.session_date <= cutoff_date,
        )
        .order_by(
            Attendance.session_date.asc(),
            Attendance.session_number.asc(),
        )
    ).all()

    if not attendance_records:
        raise ValueError(
            "Insufficient historical attendance records "
            "to generate a reliable prediction."
        )

    # Overall attendance percentage.
    attendance_percentage = _attendance_percentage(
        attendance_records
    )

    # --------------------------------------------------
    # 6. CALCULATE RECENT AND PREVIOUS 60-DAY ATTENDANCE
    # --------------------------------------------------

    recent_start = cutoff_date - timedelta(days=60)
    previous_start = cutoff_date - timedelta(days=120)

    recent_records = [
        record
        for record in attendance_records
        if recent_start < record.session_date <= cutoff_date
    ]

    previous_records = [
        record
        for record in attendance_records
        if previous_start < record.session_date <= recent_start
    ]

    attendance_recent_60d = _attendance_percentage(
        recent_records
    )

    attendance_previous_60d = _attendance_percentage(
        previous_records
    )

    attendance_trend = (
        attendance_recent_60d
        - attendance_previous_60d
    )

    attendance_sessions_to_date = len(
        attendance_records
    )

    # --------------------------------------------------
    # 7. RETURN EXACT MODEL INPUT FEATURES
    # --------------------------------------------------

    features = {
        "previous_exam_percentage": previous_exam_percentage,
        "historical_average_percentage": historical_average_percentage,
        "marks_trend": marks_trend,
        "previous_exam_count": previous_exam_count,
        "attendance_percentage": attendance_percentage,
        "attendance_recent_60d": attendance_recent_60d,
        "attendance_previous_60d": attendance_previous_60d,
        "attendance_trend": attendance_trend,
        "attendance_sessions_to_date": attendance_sessions_to_date,
        "class_grade": class_grade,
    }

    return features
