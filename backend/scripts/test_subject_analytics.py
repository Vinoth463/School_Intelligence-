
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database.connection import SessionLocal
from app.services.subject_analytics_service import get_subject_performance


def run_test():
    db = SessionLocal()

    try:
        for period_id in [1, 2]:
            print("\n" + "=" * 65)
            print(f"SUBJECT PERFORMANCE - ACADEMIC PERIOD {period_id}")
            print("=" * 65)

            results = get_subject_performance(
                db=db,
                institution_id=1,
                academic_period_id=period_id,
            )

            if not results:
                print("No subject performance records found.")
                continue

            total_records = 0

            for subject in results:
                total_records += subject["total_mark_records"]

                grade_total = sum(
                    subject[f"grade_{grade}_count"]
                    for grade in ["a", "b", "c", "d", "e", "f"]
                )

                print(f"\nSubject: {subject['subject_name']}")
                print(f"Code: {subject['subject_code']}")
                print(f"Students evaluated: {subject['students_evaluated']}")
                print(f"Mark records: {subject['total_mark_records']}")
                print(f"Average: {subject['average_percentage']}%")
                print(f"Highest: {subject['highest_percentage']}%")
                print(f"Lowest: {subject['lowest_percentage']}%")

                print(
                    "Grade distribution:",
                    {
                        "A": subject["grade_a_count"],
                        "B": subject["grade_b_count"],
                        "C": subject["grade_c_count"],
                        "D": subject["grade_d_count"],
                        "E": subject["grade_e_count"],
                        "F": subject["grade_f_count"],
                    },
                )

                assert grade_total == subject["total_mark_records"], (
                    f"Grade count mismatch for {subject['subject_name']}"
                )

            print("\nTotal mark records:", total_records)

            assert len(results) == 6, "Expected 6 subjects"
            assert total_records == 3600, "Expected 3600 mark records"

            print("PERIOD TEST PASSED")

    finally:
        db.close()


if __name__ == "__main__":
    run_test()
