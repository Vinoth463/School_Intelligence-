
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database.connection import SessionLocal
from app.services.attendance_performance_service import (
    get_attendance_performance_analysis,
)


db = SessionLocal()

try:
    for period_id in [1, 2]:

        print("\n" + "=" * 70)
        print(f"ATTENDANCE VS ACADEMIC PERFORMANCE - PERIOD {period_id}")
        print("=" * 70)

        result = get_attendance_performance_analysis(
            db=db,
            institution_id=1,
            academic_period_id=period_id,
        )

        records = result["student_records"]

        print("\n1. SUMMARY")
        print(
            "Students analyzed:",
            result["total_students_analyzed"],
        )
        print(
            "Attendance-performance correlation:",
            result["attendance_performance_correlation"],
        )
        print(
            "Correlation interpretation:",
            result["correlation_interpretation"],
        )

        print("\n2. PERFORMANCE CATEGORIES")
        print(
            "High attendance + low performance:",
            result["high_attendance_low_performance_count"],
        )
        print(
            "Low attendance + high performance:",
            result["low_attendance_high_performance_count"],
        )

        print("\n3. HIGH ATTENDANCE + LOW PERFORMANCE")

        for row in result["high_attendance_low_performance"][:10]:
            print(
                f'{row["admission_number"]} | '
                f'Attendance: {row["attendance_percentage"]}% | '
                f'Marks: {row["performance_percentage"]}%'
            )

        print("\n4. LOW ATTENDANCE + HIGH PERFORMANCE")

        for row in result["low_attendance_high_performance"][:10]:
            print(
                f'{row["admission_number"]} | '
                f'Attendance: {row["attendance_percentage"]}% | '
                f'Marks: {row["performance_percentage"]}%'
            )

        print("\n5. SAMPLE STUDENT RECORDS")

        for row in records[:5]:
            print(
                f'{row["admission_number"]} | '
                f'Class: {row["class_id"]} | '
                f'Attendance: {row["attendance_percentage"]}% | '
                f'Marks: {row["performance_percentage"]}% | '
                f'Category: {row["analysis_category"]}'
            )

        # Basic validation
        assert len(records) == 200, (
            f"Expected 200 students, got {len(records)}"
        )

        assert all(
            0 <= float(row["attendance_percentage"]) <= 100
            for row in records
        ), "Invalid attendance percentage"

        assert all(
            0 <= float(row["performance_percentage"]) <= 100
            for row in records
        ), "Invalid academic performance percentage"

        assert all(
            row["analysis_category"] in {
                "high_attendance_low_performance",
                "low_attendance_high_performance",
                "other",
            }
            for row in records
        ), "Unexpected analysis category"

        print("\nVALIDATION: PASSED")


finally:
    db.close()
    print("\nDatabase session closed.")
