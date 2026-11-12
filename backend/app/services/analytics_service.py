from sqlalchemy import text
from sqlalchemy.orm import Session


def get_dashboard_overview(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
) -> dict:
    """
    Return institution-level academic dashboard KPIs.

    All metrics are calculated from PostgreSQL.
    """
    params = {"institution_id": institution_id}

    if academic_period_id is None:
        period_filter = ""
        student_query = text("""
            SELECT COUNT(DISTINCT s.id)
            FROM students s
            JOIN classes c ON c.id = s.class_id
            WHERE s.institution_id = :institution_id
              AND s.status = 'active'
        """)
    else:
        period_filter = "AND c.academic_period_id = :academic_period_id"
        params["academic_period_id"] = academic_period_id
        student_query = text("""
            SELECT COUNT(DISTINCT s.id)
            FROM students s
            WHERE s.institution_id = :institution_id
              AND s.status = 'active'
              AND (
                  EXISTS (
                      SELECT 1
                      FROM marks m
                      JOIN classes c ON c.id = m.class_id
                      WHERE m.student_id = s.id
                        AND c.academic_period_id = :academic_period_id
                  )
                  OR EXISTS (
                      SELECT 1
                      FROM attendance a
                      JOIN classes c ON c.id = a.class_id
                      WHERE a.student_id = s.id
                        AND c.academic_period_id = :academic_period_id
                  )
              )
        """)

    marks_query = text(f"""
        SELECT
            COALESCE(
                AVG((m.obtained_marks / m.max_marks) * 100),
                0
            ) AS average_percentage,
            COUNT(*) AS total_mark_records
        FROM marks m
        JOIN examinations e ON e.id = m.examination_id
        JOIN classes c ON c.id = m.class_id
        WHERE c.institution_id = :institution_id
          AND e.academic_period_id = c.academic_period_id
          {period_filter}
    """)

    attendance_query = text(f"""
        SELECT
            COUNT(*) AS total_sessions,
            COUNT(*) FILTER (WHERE a.status = 'present')
                AS present_sessions
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        JOIN classes c ON c.id = a.class_id
        WHERE s.institution_id = :institution_id
          {period_filter}
    """)

    with db.no_autoflush:
        total_students = db.execute(
            student_query, params
        ).scalar_one()

        marks_result = db.execute(
            marks_query, params
        ).mappings().one()

        attendance_result = db.execute(
            attendance_query, params
        ).mappings().one()

    total_sessions = attendance_result["total_sessions"]
    present_sessions = attendance_result["present_sessions"]

    attendance_percentage = (
        (present_sessions / total_sessions) * 100
        if total_sessions
        else 0.0
    )

    return {
        "institution_id": institution_id,
        "academic_period_id": academic_period_id,
        "total_students": total_students,
        "average_performance_percentage": round(
            float(marks_result["average_percentage"]), 2
        ),
        "total_mark_records": marks_result["total_mark_records"],
        "total_attendance_sessions": total_sessions,
        "present_attendance_sessions": present_sessions,
        "attendance_percentage": round(
            attendance_percentage, 2
        ),
    }