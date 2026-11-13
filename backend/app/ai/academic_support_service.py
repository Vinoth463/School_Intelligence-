
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_students_with_low_marks_and_attendance(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    class_id: int | None = None,
    subject_id: int | None = None,
    marks_threshold: float = 40.0,
    attendance_threshold: float = 75.0,
) -> list[dict]:
    """
    Find students who meet BOTH conditions in the same subject:

    1. Subject marks percentage is below marks_threshold.
    2. Subject attendance percentage is below attendance_threshold.

    Marks are calculated using all available examination records
    for the selected academic period.
    """

    query = text("""
        WITH student_marks AS (
            SELECT
                s.id AS student_id,
                s.admission_number,
                s.first_name,
                s.last_name,

                c.id AS class_id,
                c.grade,
                c.section,
                c.academic_period_id,

                sub.id AS subject_id,
                sub.name AS subject_name,
                sub.code AS subject_code,

                COUNT(DISTINCT e.id) AS examinations_recorded,

                SUM(m.obtained_marks) AS total_obtained_marks,
                SUM(m.max_marks) AS total_max_marks,

                ROUND(
                    (
                        SUM(m.obtained_marks)
                        / NULLIF(SUM(m.max_marks), 0)
                    )::numeric * 100,
                    2
                ) AS marks_percentage

            FROM students s

            JOIN marks m
                ON m.student_id = s.id

            JOIN examinations e
                ON e.id = m.examination_id

            JOIN subjects sub
                ON sub.id = m.subject_id

            JOIN classes c
                ON c.id = m.class_id

            WHERE
                s.institution_id = :institution_id
                AND sub.institution_id = :institution_id
                AND c.institution_id = :institution_id
                AND e.institution_id = :institution_id
                AND e.academic_period_id = c.academic_period_id

                AND (
                    :academic_period_id IS NULL
                    OR c.academic_period_id = :academic_period_id
                )

                AND (
                    :class_id IS NULL
                    OR c.id = :class_id
                )

                AND (
                    :subject_id IS NULL
                    OR sub.id = :subject_id
                )

            GROUP BY
                s.id,
                s.admission_number,
                s.first_name,
                s.last_name,
                c.id,
                c.grade,
                c.section,
                c.academic_period_id,
                sub.id,
                sub.name,
                sub.code
        ),

        student_attendance AS (
            SELECT
                a.student_id,
                a.class_id,
                a.subject_id,

                COUNT(a.id) AS total_sessions,

                COUNT(a.id) FILTER (
                    WHERE a.status = 'present'
                ) AS present_sessions,

                COUNT(a.id) FILTER (
                    WHERE a.status = 'absent'
                ) AS absent_sessions,

                ROUND(
                    (
                        COUNT(a.id) FILTER (
                            WHERE a.status = 'present'
                        )::numeric
                        / NULLIF(COUNT(a.id), 0)
                    ) * 100,
                    2
                ) AS attendance_percentage

            FROM attendance a

            JOIN students s
                ON s.id = a.student_id

            JOIN classes c
                ON c.id = a.class_id

            JOIN subjects sub
                ON sub.id = a.subject_id

            WHERE
                s.institution_id = :institution_id
                AND c.institution_id = :institution_id
                AND sub.institution_id = :institution_id

                AND (
                    :academic_period_id IS NULL
                    OR c.academic_period_id = :academic_period_id
                )

                AND (
                    :class_id IS NULL
                    OR c.id = :class_id
                )

                AND (
                    :subject_id IS NULL
                    OR sub.id = :subject_id
                )

            GROUP BY
                a.student_id,
                a.class_id,
                a.subject_id
        )

        SELECT
            m.student_id,
            m.admission_number,
            m.first_name,
            m.last_name,

            m.class_id,
            m.grade,
            m.section,
            m.academic_period_id,

            m.subject_id,
            m.subject_name,
            m.subject_code,

            m.examinations_recorded,
            m.total_obtained_marks,
            m.total_max_marks,
            m.marks_percentage,

            a.total_sessions,
            a.present_sessions,
            a.absent_sessions,
            a.attendance_percentage

        FROM student_marks m

        JOIN student_attendance a
            ON a.student_id = m.student_id
            AND a.class_id = m.class_id
            AND a.subject_id = m.subject_id

        WHERE
            m.marks_percentage < :marks_threshold
            AND a.attendance_percentage < :attendance_threshold

        ORDER BY
            m.marks_percentage ASC,
            a.attendance_percentage ASC,
            m.admission_number ASC
    """)

    with db.no_autoflush:
        rows = db.execute(
            query,
            {
                "institution_id": institution_id,
                "academic_period_id": academic_period_id,
                "class_id": class_id,
                "subject_id": subject_id,
                "marks_threshold": marks_threshold,
                "attendance_threshold": attendance_threshold,
            },
        ).mappings().all()

    return [dict(row) for row in rows]
