
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_class_performance(
    db: Session,
    institution_id: int,
    academic_period_id: int | None = None,
    examination_id: int | None = None,
) -> list[dict]:
    """
    Calculate class-wise academic performance.

    Includes:
    - Class-level performance
    - Number of students evaluated
    - Total mark records
    - Average, highest and lowest percentages
    - Subject-wise performance

    All queries are restricted to the current institution.
    """

    conditions = [
        "c.institution_id = :institution_id",
        "e.institution_id = :institution_id",
        "s.institution_id = :institution_id",
        "sub.institution_id = :institution_id",
        "e.academic_period_id = c.academic_period_id",
    ]

    params = {
        "institution_id": institution_id,
    }

    if academic_period_id is not None:
        conditions.append(
            "c.academic_period_id = :academic_period_id"
        )
        params["academic_period_id"] = academic_period_id

    if examination_id is not None:
        conditions.append(
            "m.examination_id = :examination_id"
        )
        params["examination_id"] = examination_id

    where_clause = " AND ".join(conditions)

    query = text(f"""
        WITH filtered_marks AS (
            SELECT
                m.class_id,
                m.student_id,
                m.subject_id,
                m.examination_id,
                (m.obtained_marks / NULLIF(m.max_marks, 0)) * 100
                    AS percentage
            FROM marks m

            JOIN classes c
                ON c.id = m.class_id

            JOIN students s
                ON s.id = m.student_id

            JOIN subjects sub
                ON sub.id = m.subject_id

            JOIN examinations e
                ON e.id = m.examination_id

            WHERE {where_clause}
        ),

        class_summary AS (
            SELECT
                class_id,
                COUNT(*) AS total_mark_records,
                COUNT(DISTINCT student_id) AS students_evaluated,

                ROUND(
                    AVG(percentage)::numeric,
                    2
                ) AS average_percentage,

                ROUND(
                    MAX(percentage)::numeric,
                    2
                ) AS highest_percentage,

                ROUND(
                    MIN(percentage)::numeric,
                    2
                ) AS lowest_percentage

            FROM filtered_marks
            GROUP BY class_id
        ),

        subject_summary AS (
            SELECT
                class_id,
                subject_id,
                COUNT(*) AS total_mark_records,
                COUNT(DISTINCT student_id) AS students_evaluated,

                ROUND(
                    AVG(percentage)::numeric,
                    2
                ) AS average_percentage,

                ROUND(
                    MAX(percentage)::numeric,
                    2
                ) AS highest_percentage,

                ROUND(
                    MIN(percentage)::numeric,
                    2
                ) AS lowest_percentage

            FROM filtered_marks
            GROUP BY class_id, subject_id
        )

        SELECT
            c.id AS class_id,
            c.grade,
            c.section,
            c.academic_period_id,

            cs.total_mark_records,
            cs.students_evaluated,
            cs.average_percentage,
            cs.highest_percentage,
            cs.lowest_percentage,

            ss.subject_id,
            sub.name AS subject_name,
            sub.code AS subject_code,

            ss.total_mark_records AS subject_total_mark_records,
            ss.students_evaluated AS subject_students_evaluated,
            ss.average_percentage AS subject_average_percentage,
            ss.highest_percentage AS subject_highest_percentage,
            ss.lowest_percentage AS subject_lowest_percentage

        FROM class_summary cs

        JOIN classes c
            ON c.id = cs.class_id

        JOIN subject_summary ss
            ON ss.class_id = cs.class_id

        JOIN subjects sub
            ON sub.id = ss.subject_id

        ORDER BY
            c.grade ASC,
            c.section ASC,
            sub.name ASC
    """)

    with db.no_autoflush:
        rows = db.execute(
            query,
            params,
        ).mappings().all()

    class_lookup = {}

    for row in rows:
        class_id = row["class_id"]

        if class_id not in class_lookup:
            class_lookup[class_id] = {
                "class_id": class_id,
                "grade": row["grade"],
                "section": row["section"],
                "academic_period_id": row["academic_period_id"],
                "total_mark_records": row["total_mark_records"],
                "students_evaluated": row["students_evaluated"],
                "average_percentage": float(row["average_percentage"]),
                "highest_percentage": float(row["highest_percentage"]),
                "lowest_percentage": float(row["lowest_percentage"]),
                "subjects": [],
            }

        class_lookup[class_id]["subjects"].append({
            "subject_id": row["subject_id"],
            "subject_name": row["subject_name"],
            "subject_code": row["subject_code"],
            "total_mark_records": row["subject_total_mark_records"],
            "students_evaluated": row["subject_students_evaluated"],
            "average_percentage": float(
                row["subject_average_percentage"]
            ),
            "highest_percentage": float(
                row["subject_highest_percentage"]
            ),
            "lowest_percentage": float(
                row["subject_lowest_percentage"]
            ),
        })

    return list(class_lookup.values())
