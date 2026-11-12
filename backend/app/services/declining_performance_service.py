
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_declining_performance(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    class_id: int | None = None,
    decline_threshold: float = 0.0,
) -> list[dict]:
    """
    Identify students whose overall performance decreases
    between consecutive examinations.

    decline_threshold:
        Minimum percentage-point decrease to report.
        Default 0.0 means report every decline.
    """

    conditions = [
        "s.institution_id = :institution_id",
        "e.institution_id = :institution_id",
        "sub.institution_id = :institution_id",
        "c.institution_id = :institution_id",
        "e.academic_period_id = c.academic_period_id",
        "s.id = m.student_id",
    ]

    params = {
        "institution_id": institution_id,
        "decline_threshold": decline_threshold,
    }

    if academic_period_id is not None:
        conditions.append(
            "e.academic_period_id = :academic_period_id"
        )
        params["academic_period_id"] = academic_period_id

    if class_id is not None:
        conditions.append("m.class_id = :class_id")
        params["class_id"] = class_id

    where_clause = " AND ".join(conditions)

    query = text(f"""
        WITH examination_performance AS (
            SELECT
                s.id AS student_id,
                s.admission_number,
                s.first_name,
                s.last_name,
                e.id AS examination_id,
                e.name AS examination_name,
                e.academic_period_id,
                e.exam_date,
                m.class_id,
                SUM(m.obtained_marks) AS total_obtained_marks,
                SUM(m.max_marks) AS total_max_marks,
                ROUND(
                    (
                        SUM(m.obtained_marks)
                        / NULLIF(SUM(m.max_marks), 0)
                    )::numeric * 100,
                    2
                ) AS overall_percentage
            FROM students s
            JOIN marks m
                ON m.student_id = s.id
            JOIN examinations e
                ON e.id = m.examination_id
            JOIN subjects sub
                ON sub.id = m.subject_id
            JOIN classes c
                ON c.id = m.class_id
            WHERE {where_clause}
            GROUP BY
                s.id,
                s.admission_number,
                s.first_name,
                s.last_name,
                e.id,
                e.name,
                e.academic_period_id,
                e.exam_date,
                m.class_id
        ),
        performance_changes AS (
            SELECT
                *,
                LAG(examination_id) OVER (
                    PARTITION BY
                        student_id,
                        academic_period_id,
                        class_id
                    ORDER BY exam_date, examination_id
                ) AS previous_examination_id,
                LAG(examination_name) OVER (
                    PARTITION BY
                        student_id,
                        academic_period_id,
                        class_id
                    ORDER BY exam_date, examination_id
                ) AS previous_examination_name,
                LAG(overall_percentage) OVER (
                    PARTITION BY
                        student_id,
                        academic_period_id,
                        class_id
                    ORDER BY exam_date, examination_id
                ) AS previous_percentage
            FROM examination_performance
        )
        SELECT
            student_id,
            admission_number,
            first_name,
            last_name,
            academic_period_id,
            class_id,
            previous_examination_id,
            previous_examination_name,
            examination_id,
            examination_name,
            previous_percentage,
            overall_percentage AS current_percentage,
            ROUND(
                (
                    overall_percentage - previous_percentage
                )::numeric,
                2
            ) AS percentage_change,
            CASE
                WHEN overall_percentage < previous_percentage
                    THEN 'declining'
                WHEN overall_percentage > previous_percentage
                    THEN 'improving'
                ELSE 'unchanged'
            END AS performance_status
        FROM performance_changes
        WHERE previous_percentage IS NOT NULL
            AND overall_percentage < previous_percentage
            AND previous_percentage - overall_percentage
                >= :decline_threshold
        ORDER BY
            percentage_change ASC,
            student_id ASC
    """)

    with db.no_autoflush:
        rows = db.execute(query, params).mappings().all()

    return [dict(row) for row in rows]


def get_subject_declines(
    db: Session,
    institution_id: int,
    academic_period_id: int,
    student_id: int | None = None,
) -> list[dict]:
    """
    Identify subject-wise declines between consecutive
    examinations within one academic period.
    """

    conditions = [
        "s.institution_id = :institution_id",
        "sub.institution_id = :institution_id",
        "e.institution_id = :institution_id",
        "c.institution_id = :institution_id",
        "e.academic_period_id = :academic_period_id",
        "e.academic_period_id = c.academic_period_id",
    ]

    params = {
        "institution_id": institution_id,
        "academic_period_id": academic_period_id,
    }

    if student_id is not None:
        conditions.append("s.id = :student_id")
        params["student_id"] = student_id

    where_clause = " AND ".join(conditions)

    query = text(f"""
        WITH subject_performance AS (
            SELECT
                s.id AS student_id,
                s.admission_number,
                s.first_name,
                s.last_name,
                sub.id AS subject_id,
                sub.name AS subject_name,
                sub.code AS subject_code,
                e.id AS examination_id,
                e.name AS examination_name,
                e.exam_date,
                e.academic_period_id,
                m.class_id,
                ROUND(
                    (
                        SUM(m.obtained_marks)
                        / NULLIF(SUM(m.max_marks), 0)
                    )::numeric * 100,
                    2
                ) AS subject_percentage
            FROM students s
            JOIN marks m
                ON m.student_id = s.id
            JOIN examinations e
                ON e.id = m.examination_id
            JOIN subjects sub
                ON sub.id = m.subject_id
            JOIN classes c
                ON c.id = m.class_id
            WHERE {where_clause}
            GROUP BY
                s.id,
                s.admission_number,
                s.first_name,
                s.last_name,
                sub.id,
                sub.name,
                sub.code,
                e.id,
                e.name,
                e.exam_date,
                e.academic_period_id,
                m.class_id
        ),
        subject_changes AS (
            SELECT
                *,
                LAG(subject_percentage) OVER (
                    PARTITION BY
                        student_id,
                        subject_id,
                        academic_period_id,
                        class_id
                    ORDER BY exam_date, examination_id
                ) AS previous_percentage,
                LAG(examination_name) OVER (
                    PARTITION BY
                        student_id,
                        subject_id,
                        academic_period_id,
                        class_id
                    ORDER BY exam_date, examination_id
                ) AS previous_examination_name
            FROM subject_performance
        )
        SELECT
            student_id,
            admission_number,
            first_name,
            last_name,
            subject_id,
            subject_name,
            subject_code,
            previous_examination_name,
            examination_name,
            previous_percentage,
            subject_percentage AS current_percentage,
            ROUND(
                (
                    subject_percentage - previous_percentage
                )::numeric,
                2
            ) AS percentage_change
        FROM subject_changes
        WHERE previous_percentage IS NOT NULL
            AND subject_percentage < previous_percentage
        ORDER BY
            percentage_change ASC,
            student_id ASC,
            subject_name ASC
    """)

    with db.no_autoflush:
        rows = db.execute(query, params).mappings().all()

    return [dict(row) for row in rows]
