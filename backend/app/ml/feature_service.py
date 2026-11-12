
from datetime import date, timedelta
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.marks import Mark
from app.models.attendance import Attendance
from app.models.examination import Examination
from app.models.classroom import Classroom
from app.models.subject import Subject
from app.models.academic_period import AcademicPeriod


def _attendance_percentage(records):
    """
    Calculate attendance percentage.

    Return None when no attendance records exist.
    The trained model's numerical imputer handles missing values.
    """

    if not records:
        return None

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
    Build historical features using the same definitions
    as the original ML training pipeline.

    Only completed historical marks and attendance records
    are used. Future information is excluded.
    """

    today = date.today()

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
    # 2. VALIDATE SUBJECT
    # --------------------------------------------------

    subject = db.scalar(
        select(Subject).where(
            Subject.id == subject_id,
            Subject.institution_id == institution_id,
        )
    )

    if subject is None:
        raise ValueError(
            "Subject not found in this institution."
        )

    # --------------------------------------------------
    # 3. VALIDATE TARGET EXAMINATION AND PERIOD
    # --------------------------------------------------

    target_result = db.execute(
        select(Examination, AcademicPeriod)
        .join(
            AcademicPeriod,
            Examination.academic_period_id == AcademicPeriod.id,
        )
        .where(
            Examination.id == target_examination_id,
            Examination.institution_id == institution_id,
            AcademicPeriod.institution_id == institution_id,
        )
    ).first()

    if target_result is None:
        raise ValueError(
            "Target examination not found in this institution."
        )

    target_exam, target_period = target_result

    if target_exam.exam_date <= today:
        raise ValueError(
            "Target examination must be in the future."
        )

    if not (
        target_period.start_date
        <= target_exam.exam_date
        <= target_period.end_date
    ):
        raise ValueError(
            "Target examination date is outside its academic period."
        )

    # --------------------------------------------------
    # 4. VALIDATE STUDENT'S TARGET CLASS
    # --------------------------------------------------

    target_class = db.scalar(
        select(Classroom).where(
            Classroom.id == student.class_id,
            Classroom.institution_id == institution_id,
            Classroom.academic_period_id
            == target_exam.academic_period_id,
        )
    )

    if target_class is None:
        raise ValueError(
            "Student's current class does not belong to "
            "the target examination's academic period."
        )

    # --------------------------------------------------
    # 5. PREVENT PREDICTION WHEN TARGET MARKS EXIST
    # --------------------------------------------------

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
    # 6. FETCH VALID HISTORICAL EXAMINATION MARKS
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
        .join(
            AcademicPeriod,
            Examination.academic_period_id == AcademicPeriod.id,
        )
        .where(
            Mark.student_id == student_id,
            Mark.subject_id == subject_id,

            Examination.institution_id == institution_id,
            Classroom.institution_id == institution_id,
            AcademicPeriod.institution_id == institution_id,

            Examination.academic_period_id
            == Classroom.academic_period_id,

            Examination.exam_date < target_exam.exam_date,
            Examination.exam_date <= today,

            Examination.exam_date >= AcademicPeriod.start_date,
            Examination.exam_date <= AcademicPeriod.end_date,
        )
        .order_by(
            Examination.exam_date.asc(),
            Examination.id.asc(),
            Mark.id.asc(),
        )
    ).all()

    if not historical_rows:
        raise ValueError(
            "Insufficient historical examination marks."
        )

    # --------------------------------------------------
    # 7. CALCULATE HISTORICAL MARK FEATURES
    # --------------------------------------------------

    previous_scores = []

    for mark, examination, classroom in historical_rows:

        max_marks = float(mark.max_marks)

        if max_marks <= 0:
            raise ValueError(
                "Historical examination contains invalid maximum marks."
            )

        percentage = (
            float(mark.obtained_marks) / max_marks
        ) * 100.0

        previous_scores.append(percentage)

    previous_exam_percentage = previous_scores[-1]

    historical_average_percentage = mean(
        previous_scores
    )

    marks_trend = (
        previous_scores[-1] - previous_scores[-2]
        if len(previous_scores) >= 2
        else None
    )

    previous_exam_count = len(previous_scores)

    latest_mark, current_exam, current_class = historical_rows[-1]

    class_grade = current_class.grade

    # The latest completed historical examination determines
    # the cutoff date for attendance feature calculation.
    cutoff_date = current_exam.exam_date

    # --------------------------------------------------
    # 8. FETCH HISTORICAL ATTENDANCE
    # --------------------------------------------------

    attendance_records = db.scalars(
        select(Attendance)
        .join(
            Student,
            Attendance.student_id == Student.id,
        )
        .join(
            Subject,
            Attendance.subject_id == Subject.id,
        )
        .join(
            Classroom,
            Attendance.class_id == Classroom.id,
        )
        .join(
            AcademicPeriod,
            Classroom.academic_period_id == AcademicPeriod.id,
        )
        .where(
            Attendance.student_id == student_id,
            Attendance.subject_id == subject_id,

            Student.institution_id == institution_id,
            Subject.institution_id == institution_id,
            Classroom.institution_id == institution_id,
            AcademicPeriod.institution_id == institution_id,

            Attendance.session_date >= student.admission_date,
            Attendance.session_date <= cutoff_date,

            Attendance.session_date >= AcademicPeriod.start_date,
            Attendance.session_date <= AcademicPeriod.end_date,
        )
        .order_by(
            Attendance.session_date.asc(),
            Attendance.session_number.asc(),
        )
    ).all()

    # Missing attendance is allowed.
    # The trained numerical imputer handles missing values.
    attendance_percentage = _attendance_percentage(
        attendance_records
    )

    # --------------------------------------------------
    # 9. CALCULATE RECENT AND PREVIOUS 60-DAY ATTENDANCE
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
        attendance_recent_60d - attendance_previous_60d
        if (
            attendance_recent_60d is not None
            and attendance_previous_60d is not None
        )
        else None
    )

    attendance_sessions_to_date = len(
        attendance_records
    )

    # --------------------------------------------------
    # 10. RETURN EXACT TRAINING FEATURES
    # --------------------------------------------------

    return {
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
