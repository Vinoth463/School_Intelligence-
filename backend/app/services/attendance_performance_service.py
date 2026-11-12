
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_attendance_performance_analysis(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    class_id: int | None = None,
    high_attendance_threshold: float = 85.0,
    low_attendance_threshold: float = 75.0,
    low_marks_threshold: float = 40.0,
    high_marks_threshold: float = 75.0,
):
    query = text("""
        WITH attendance_summary AS (
            SELECT
                a.student_id,
                a.class_id,
                c.academic_period_id,
                COUNT(*) AS total_sessions,
                COUNT(*) FILTER (
                    WHERE a.status = 'present'
                ) AS present_sessions,
                ROUND(
                    COUNT(*) FILTER (
                        WHERE a.status = 'present'
                    ) * 100.0 / NULLIF(COUNT(*), 0),
                    2
                ) AS attendance_percentage
            FROM attendance a
            JOIN classes c
                ON c.id = a.class_id
            JOIN students s
                ON s.id = a.student_id
            WHERE s.institution_id = :institution_id
              AND c.institution_id = :institution_id
            GROUP BY
                a.student_id,
                a.class_id,
                c.academic_period_id
        ),

        marks_summary AS (
            SELECT
                m.student_id,
                m.class_id,
                e.academic_period_id,
                SUM(m.obtained_marks) AS total_obtained,
                SUM(m.max_marks) AS total_maximum,
                ROUND(
                    SUM(m.obtained_marks) * 100.0 /
                    NULLIF(SUM(m.max_marks), 0),
                    2
                ) AS performance_percentage
            FROM marks m
            JOIN examinations e
                ON e.id = m.examination_id
            JOIN classes c
                ON c.id = m.class_id
            JOIN students s
                ON s.id = m.student_id
            WHERE s.institution_id = :institution_id
              AND e.institution_id = :institution_id
              AND c.institution_id = :institution_id
              AND e.academic_period_id = c.academic_period_id
            GROUP BY
                m.student_id,
                m.class_id,
                e.academic_period_id
        )

        SELECT
            s.id AS student_id,
            s.admission_number,
            s.first_name,
            s.last_name,
            a.academic_period_id,
            a.class_id,
            a.total_sessions,
            a.present_sessions,
            a.attendance_percentage,
            m.total_obtained,
            m.total_maximum,
            m.performance_percentage,

            CASE
                WHEN a.attendance_percentage >= :high_attendance_threshold
                 AND m.performance_percentage < :low_marks_threshold
                    THEN 'high_attendance_low_performance'

                WHEN a.attendance_percentage < :low_attendance_threshold
                 AND m.performance_percentage >= :high_marks_threshold
                    THEN 'low_attendance_high_performance'

                ELSE 'other'
            END AS analysis_category

        FROM attendance_summary a
        JOIN marks_summary m
            ON m.student_id = a.student_id
           AND m.class_id = a.class_id
           AND m.academic_period_id = a.academic_period_id
        JOIN students s
            ON s.id = a.student_id

        WHERE
            (:academic_period_id IS NULL
             OR a.academic_period_id = :academic_period_id)

            AND (:class_id IS NULL OR a.class_id = :class_id)

        ORDER BY
            a.academic_period_id,
            a.class_id,
            s.admission_number
    """)

    rows = db.execute(
        query,
        {
            "institution_id": institution_id,
            "academic_period_id": academic_period_id,
            "class_id": class_id,
            "high_attendance_threshold": high_attendance_threshold,
            "low_attendance_threshold": low_attendance_threshold,
            "low_marks_threshold": low_marks_threshold,
            "high_marks_threshold": high_marks_threshold,
        },
    ).mappings().all()

    results = [dict(row) for row in rows]

    correlation = None

    if len(results) >= 2:
        attendance_values = [
            float(row["attendance_percentage"])
            for row in results
        ]

        performance_values = [
            float(row["performance_percentage"])
            for row in results
        ]

        import numpy as np

        if (
            np.std(attendance_values) > 0
            and np.std(performance_values) > 0
        ):
            correlation = float(
                np.corrcoef(
                    attendance_values,
                    performance_values
                )[0, 1]
            )

    high_attendance_low_performance = [
        row for row in results
        if row["analysis_category"] == "high_attendance_low_performance"
    ]

    low_attendance_high_performance = [
        row for row in results
        if row["analysis_category"] == "low_attendance_high_performance"
    ]

    return {
        "total_students_analyzed": len(results),
        "attendance_performance_correlation": correlation,
        "correlation_interpretation": (
            "Correlation describes association, not causation."
        ),
        "high_attendance_low_performance_count": len(
            high_attendance_low_performance
        ),
        "low_attendance_high_performance_count": len(
            low_attendance_high_performance
        ),
        "high_attendance_low_performance": (
            high_attendance_low_performance
        ),
        "low_attendance_high_performance": (
            low_attendance_high_performance
        ),
        "student_records": results,
    }
