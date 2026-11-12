
from sqlalchemy import text

from app.database.connection import SessionLocal


def main():
    db = SessionLocal()

    try:
        query = text("""
            SELECT
                s.id AS student_id,
                s.admission_number,
                s.admission_date,
                COUNT(*) AS rejected_sessions,
                MIN((r.raw_data->>'session_date')::date)
                    AS first_invalid_session,
                MAX((r.raw_data->>'session_date')::date)
                    AS last_invalid_session
            FROM import_rejections r
            JOIN students s
                ON s.id = (r.raw_data->>'student_id')::integer
            WHERE r.import_log_id = 3
            GROUP BY
                s.id,
                s.admission_number,
                s.admission_date
            ORDER BY s.id
        """)

        rows = db.execute(query).all()

        print("AFFECTED STUDENTS:", len(rows))
        print("\nSTUDENT DETAILS:")

        for row in rows:
            print(
                f"Student ID: {row.student_id} | "
                f"Admission: {row.admission_number} | "
                f"Admission date: {row.admission_date} | "
                f"Rejected sessions: {row.rejected_sessions} | "
                f"First invalid session: {row.first_invalid_session} | "
                f"Last invalid session: {row.last_invalid_session}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
