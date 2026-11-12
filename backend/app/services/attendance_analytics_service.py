
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_student_attendance(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    class_id: int | None = None,
    student_id: int | None = None,
):
    query = """
        SELECT
            s.id AS student_id,
            s.admission_number,
            s.first_name,
            s.last_name,

            c.id AS class_id,
            c.grade,
            c.section,

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
            AND c.academic_period_id = :academic_period_id
            AND a.class_id = c.id

            AND (
                :class_id IS NULL
                OR a.class_id = :class_id
            )

            AND (
                :student_id IS NULL
                OR a.student_id = :student_id
            )

        GROUP BY
            s.id,
            s.admission_number,
            s.first_name,
            s.last_name,
            c.id,
            c.grade,
            c.section

        ORDER BY
            attendance_percentage ASC NULLS LAST,
            s.admission_number
    """

    if academic_period_id is None:
        query = query.replace(
            "AND c.academic_period_id = :academic_period_id",
            "",
        )

    result = db.execute(
        text(query),
        {
            "institution_id": institution_id,
            "academic_period_id": academic_period_id,
            "class_id": class_id,
            "student_id": student_id,
        },
    )

    return [dict(row) for row in result.mappings().all()]


def get_subject_attendance(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    class_id: int | None = None,
):
    query = """
        SELECT
            sub.id AS subject_id,
            sub.name AS subject_name,
            sub.code AS subject_code,

            COUNT(a.id) AS total_sessions,

            COUNT(a.id) FILTER (
                WHERE a.status = 'present'
            ) AS present_sessions,

            COUNT(a.id) FILTER (
                WHERE a.status = 'absent'
            ) AS absent_sessions,

            COUNT(DISTINCT a.student_id) AS students_recorded,

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
                OR a.class_id = :class_id
            )

        GROUP BY
            sub.id,
            sub.name,
            sub.code

        ORDER BY
            attendance_percentage ASC NULLS LAST,
            sub.name
    """

    result = db.execute(
        text(query),
        {
            "institution_id": institution_id,
            "academic_period_id": academic_period_id,
            "class_id": class_id,
        },
    )

    return [dict(row) for row in result.mappings().all()]


def get_class_attendance(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
):
    query = """
        SELECT
            c.id AS class_id,
            c.grade,
            c.section,
            c.academic_period_id,

            COUNT(a.id) AS total_sessions,

            COUNT(a.id) FILTER (
                WHERE a.status = 'present'
            ) AS present_sessions,

            COUNT(a.id) FILTER (
                WHERE a.status = 'absent'
            ) AS absent_sessions,

            COUNT(DISTINCT a.student_id) AS students_recorded,

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

        GROUP BY
            c.id,
            c.grade,
            c.section,
            c.academic_period_id

        ORDER BY
            c.grade,
            c.section
    """

    result = db.execute(
        text(query),
        {
            "institution_id": institution_id,
            "academic_period_id": academic_period_id,
        },
    )

    return [dict(row) for row in result.mappings().all()]


def get_low_attendance_students(
    db: Session,
    institution_id: int,
    threshold: float = 75.0,
    academic_period_id: int | None = None,
    class_id: int | None = None,
):
    query = """
        SELECT
            s.id AS student_id,
            s.admission_number,
            s.first_name,
            s.last_name,

            c.id AS class_id,
            c.grade,
            c.section,

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
                OR a.class_id = :class_id
            )

        GROUP BY
            s.id,
            s.admission_number,
            s.first_name,
            s.last_name,
            c.id,
            c.grade,
            c.section

        HAVING
            COUNT(a.id) > 0
            AND (
                COUNT(a.id) FILTER (
                    WHERE a.status = 'present'
                )::numeric
                / COUNT(a.id)
            ) * 100 < :threshold

        ORDER BY
            attendance_percentage ASC,
            s.admission_number
    """

    result = db.execute(
        text(query),
        {
            "institution_id": institution_id,
            "academic_period_id": academic_period_id,
            "class_id": class_id,
            "threshold": threshold,
        },
    )

    return [dict(row) for row in result.mappings().all()]
