
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database.connection import SessionLocal

from app.services.attendance_analytics_service import (
    get_student_attendance,
    get_subject_attendance,
    get_class_attendance,
    get_low_attendance_students,
)


db = SessionLocal()

try:
    for period_id in [1, 2]:
        print("\n" + "=" * 65)
        print(f"ATTENDANCE ANALYTICS - ACADEMIC PERIOD {period_id}")
        print("=" * 65)

        # 1. Student attendance
        students = get_student_attendance(
            db=db,
            institution_id=1,
            academic_period_id=period_id,
        )

        print("\n1. STUDENT ATTENDANCE")
        print("Students returned:", len(students))

        total_sessions = sum(row["total_sessions"] for row in students)
        total_present = sum(row["present_sessions"] for row in students)
        total_absent = sum(row["absent_sessions"] for row in students)

        print("Total sessions:", total_sessions)
        print("Present sessions:", total_present)
        print("Absent sessions:", total_absent)

        if total_sessions:
            print(
                "Overall attendance percentage:",
                round(total_present / total_sessions * 100, 2),
            )

        student_one = get_student_attendance(
            db=db,
            institution_id=1,
            academic_period_id=period_id,
            student_id=1,
        )

        print("\nStudent ID 1 attendance:")
        for row in student_one:
            print(
                f'{row["admission_number"]} | '
                f'{row["grade"]}-{row["section"]} | '
                f'Present: {row["present_sessions"]} | '
                f'Absent: {row["absent_sessions"]} | '
                f'Attendance: {row["attendance_percentage"]}%'
            )

        # 2. Subject attendance
        subjects = get_subject_attendance(
            db=db,
            institution_id=1,
            academic_period_id=period_id,
        )

        print("\n2. SUBJECT ATTENDANCE")
        print("Subjects returned:", len(subjects))

        for row in subjects:
            print(
                f'{row["subject_name"]} | '
                f'Sessions: {row["total_sessions"]} | '
                f'Present: {row["present_sessions"]} | '
                f'Attendance: {row["attendance_percentage"]}%'
            )

        # 3. Class attendance
        classes = get_class_attendance(
            db=db,
            institution_id=1,
            academic_period_id=period_id,
        )

        print("\n3. CLASS ATTENDANCE")
        print("Classes returned:", len(classes))

        for row in classes:
            print(
                f'{row["grade"]}-{row["section"]} | '
                f'Students recorded: {row["students_recorded"]} | '
                f'Sessions: {row["total_sessions"]} | '
                f'Attendance: {row["attendance_percentage"]}%'
            )

        # 4. Low attendance
        low_attendance = get_low_attendance_students(
            db=db,
            institution_id=1,
            academic_period_id=period_id,
            threshold=75.0,
        )

        print("\n4. LOW ATTENDANCE STUDENTS")
        print("Threshold: Below 75%")
        print("Students identified:", len(low_attendance))

        for row in low_attendance[:10]:
            print(
                f'{row["admission_number"]} | '
                f'{row["grade"]}-{row["section"]} | '
                f'Attendance: {row["attendance_percentage"]}%'
            )

finally:
    db.close()
    print("\nDatabase session closed.")
