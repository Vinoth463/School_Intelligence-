
import sys
from pathlib import Path

# Add the backend root directory to Python's import path.
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select, func

from app.database.connection import SessionLocal
from app.models import (
    AcademicPeriod,
    Classroom,
    Examination,
    Student,
    Subject,
    Attendance,
)


def main():
    db = SessionLocal()

    try:
        print("\n========== ACADEMIC PERIODS AND CLASSES ==========")

        rows = db.execute(
            select(Classroom, AcademicPeriod)
            .join(
                AcademicPeriod,
                Classroom.academic_period_id == AcademicPeriod.id,
            )
            .order_by(AcademicPeriod.start_date, Classroom.id)
        ).all()

        for classroom, period in rows:
            print(
                f"Class ID: {classroom.id} | "
                f"Period ID: {period.id} | "
                f"Start: {period.start_date} | "
                f"End: {period.end_date}"
            )

        print("\n========== SUBJECTS ==========")

        subjects = db.scalars(
            select(Subject).order_by(Subject.id)
        ).all()

        for subject in subjects:
            print(
                f"Subject ID: {subject.id} | "
                f"Name: {subject.name}"
            )

        print("\n========== EXAMINATIONS ==========")

        examinations = db.scalars(
            select(Examination).order_by(Examination.exam_date)
        ).all()

        for exam in examinations:
            print(
                f"Exam ID: {exam.id} | "
                f"Period ID: {exam.academic_period_id} | "
                f"Date: {exam.exam_date}"
            )

        print("\n========== STUDENT INFORMATION ==========")

        print(
            "Current student count:",
            db.scalar(
                select(func.count()).select_from(Student)
            ),
        )

        print(
            "Maximum student ID:",
            db.scalar(select(func.max(Student.id))),
        )

        print(
            "Maximum attendance date:",
            db.scalar(select(func.max(Attendance.session_date))),
        )

        print("\nDatabase inspection completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
