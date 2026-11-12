
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database.connection import SessionLocal
from app.models.examination import Examination
from app.models.academic_period import AcademicPeriod
from app.models.marks import Mark


def main():
    db = SessionLocal()

    try:
        periods = (
            db.query(AcademicPeriod)
            .filter(AcademicPeriod.institution_id == 1)
            .order_by(AcademicPeriod.start_date)
            .all()
        )

        print("\nACADEMIC PERIODS")
        print("-" * 60)

        for period in periods:
            print(
                f"ID: {period.id} | "
                f"Name: {period.name} | "
                f"Start: {period.start_date} | "
                f"End: {period.end_date}"
            )

        examinations = (
            db.query(Examination)
            .filter(Examination.institution_id == 1)
            .order_by(Examination.exam_date)
            .all()
        )

        print("\nEXAMINATIONS AND MARK COUNTS")
        print("-" * 60)

        for exam in examinations:
            mark_count = (
                db.query(Mark)
                .filter(Mark.examination_id == exam.id)
                .count()
            )

            print(
                f"ID: {exam.id} | "
                f"Name: {exam.name} | "
                f"Period ID: {exam.academic_period_id} | "
                f"Date: {exam.exam_date} | "
                f"Marks: {mark_count}"
            )

    except Exception:
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
