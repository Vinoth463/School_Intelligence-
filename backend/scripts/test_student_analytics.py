
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models import Student
from app.services.student_analytics_service import get_student_performance


def run_test():
    db = SessionLocal()

    try:
        student = db.execute(
            select(Student)
            .where(
                Student.institution_id == 1,
                Student.status == "active",
            )
            .order_by(Student.id)
            .limit(1)
        ).scalar_one_or_none()

        if student is None:
            raise RuntimeError("No active student found.")

        print("=" * 65)
        print("STUDENT ANALYTICS TEST")
        print("=" * 65)

        print("Student ID:", student.id)
        print("Admission Number:", student.admission_number)
        print("Name:", student.first_name, student.last_name)

        for period_id in [1, 2]:

            print("\n" + "-" * 65)
            print(f"ACADEMIC PERIOD {period_id}")
            print("-" * 65)

            result = get_student_performance(
                db=db,
                institution_id=1,
                student_id=student.id,
                academic_period_id=period_id,
            )

            if result is None:
                print("No performance records found.")
                continue

            print("\nExaminations:", len(result["examinations"]))

            for exam in result["examinations"]:
                print("\nExamination:", exam["examination_name"])
                print("Date:", exam["exam_date"])
                print("Subjects:", len(exam["subjects"]))
                print(
                    "Total Marks:",
                    exam["total_obtained_marks"],
                    "/",
                    exam["total_max_marks"],
                )
                print(
                    "Overall Percentage:",
                    exam["overall_percentage"],
                    "%",
                )

                for subject in exam["subjects"]:
                    print(
                        f"  {subject['subject_name']}: "
                        f"{subject['obtained_marks']}/"
                        f"{subject['max_marks']} "
                        f"({subject['percentage']}%)"
                    )

            print("\nPerformance Trend:")

            for item in result["performance_trend"]:
                print(
                    item["examination_name"],
                    "|",
                    item["overall_percentage"],
                    "%",
                    "| Change:",
                    item["change_from_previous"],
                )

            assert len(result["examinations"]) == 3, (
                "Expected 3 examinations per academic period"
            )

            for exam in result["examinations"]:
                assert len(exam["subjects"]) == 6, (
                    "Expected 6 subjects per examination"
                )

            print("\nPERIOD TEST PASSED")

    finally:
        db.close()


if __name__ == "__main__":
    run_test()
