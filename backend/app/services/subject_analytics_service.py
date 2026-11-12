
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_subject_performance(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    examination_id: int | None = None,
    class_id: int | None = None,
) -> list[dict]:
    """
    Calculate subject-wise academic performance.

    Filters:
    - Institution (mandatory)
    - Academic period (optional)
    - Examination (optional)
    - Class (optional)
    """

    conditions = [
        "s.institution_id = :institution_id",
        "c.institution_id = :institution_id",
        "e.institution_id = :institution_id",
        "e.academic_period_id = c.academic_period_id",
    ]

    params = {"institution_id": institution_id}

    if academic_period_id is not None:
        conditions.append(
            "e.academic_period_id = :academic_period_id"
        )
        params["academic_period_id"] = academic_period_id

    if examination_id is not None:
        conditions.append(
            "m.examination_id = :examination_id"
        )
        params["examination_id"] = examination_id

    if class_id is not None:
        conditions.append(
            "m.class_id = :class_id"
        )
        params["class_id"] = class_id

    where_clause = " AND ".join(conditions)

    query = text(f"""
        SELECT
            s.id AS subject_id,
            s.name AS subject_name,
            s.code AS subject_code,

            COUNT(*) AS total_mark_records,
            COUNT(DISTINCT m.student_id) AS students_evaluated,

            ROUND(
                AVG(
                    (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100
                )::numeric,
                2
            ) AS average_percentage,

            ROUND(
                MAX(
                    (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100
                )::numeric,
                2
            ) AS highest_percentage,

            ROUND(
                MIN(
                    (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100
                )::numeric,
                2
            ) AS lowest_percentage,

            COUNT(*) FILTER (
                WHERE (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 >= 90
            ) AS grade_a_count,

            COUNT(*) FILTER (
                WHERE (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 >= 80
                  AND (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 < 90
            ) AS grade_b_count,

            COUNT(*) FILTER (
                WHERE (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 >= 70
                  AND (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 < 80
            ) AS grade_c_count,

            COUNT(*) FILTER (
                WHERE (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 >= 60
                  AND (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 < 70
            ) AS grade_d_count,

            COUNT(*) FILTER (
                WHERE (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 >= 40
                  AND (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 < 60
            ) AS grade_e_count,

            COUNT(*) FILTER (
                WHERE (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100 < 40
            ) AS grade_f_count

        FROM marks m

        JOIN subjects s
            ON s.id = m.subject_id

        JOIN classes c
            ON c.id = m.class_id

        JOIN examinations e
            ON e.id = m.examination_id

        WHERE {where_clause}

        GROUP BY
            s.id,
            s.name,
            s.code

        ORDER BY
            average_percentage DESC,
            s.name ASC
    """)

    with db.no_autoflush:
        rows = db.execute(query, params).mappings().all()

    return [dict(row) for row in rows]
