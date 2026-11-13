
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_examination_comparison(
    db: Session,
    institution_id: int,
    academic_period_id: int,
    class_id: int | None = None,
    subject_id: int | None = None,
) -> dict:
    """
    Compare academic performance across examinations.

    Results are ordered by examination date.
    Changes are calculated against the previous available
    examination for the same filter combination.
    """

    conditions = [
        "c.institution_id = :institution_id",
        "e.institution_id = :institution_id",
        "s.institution_id = :institution_id",
        "sub.institution_id = :institution_id",
        "e.academic_period_id = :academic_period_id",
        "c.academic_period_id = e.academic_period_id",
    ]

    params = {
        "institution_id": institution_id,
        "academic_period_id": academic_period_id,
    }

    if class_id is not None:
        conditions.append("m.class_id = :class_id")
        params["class_id"] = class_id

    if subject_id is not None:
        conditions.append("m.subject_id = :subject_id")
        params["subject_id"] = subject_id

    where_clause = " AND ".join(conditions)

    query = text(f"""
        WITH filtered_marks AS (
            SELECT
                e.id AS examination_id,
                e.name AS examination_name,
                e.exam_date,
                m.student_id,
                m.subject_id,
                sub.name AS subject_name,
                sub.code AS subject_code,
                (
                    m.obtained_marks
                    / NULLIF(m.max_marks, 0)
                ) * 100 AS percentage

            FROM marks m

            JOIN examinations e
                ON e.id = m.examination_id

            JOIN classes c
                ON c.id = m.class_id

            JOIN students s
                ON s.id = m.student_id

            JOIN subjects sub
                ON sub.id = m.subject_id

            WHERE {where_clause}
        ),

        examination_summary AS (
            SELECT
                examination_id,
                examination_name,
                exam_date,

                COUNT(*) AS total_mark_records,
                COUNT(DISTINCT student_id) AS students_evaluated,

                ROUND(AVG(percentage)::numeric, 2)
                    AS average_percentage,

                ROUND(MAX(percentage)::numeric, 2)
                    AS highest_percentage,

                ROUND(MIN(percentage)::numeric, 2)
                    AS lowest_percentage

            FROM filtered_marks

            GROUP BY
                examination_id,
                examination_name,
                exam_date
        ),

        subject_summary AS (
            SELECT
                examination_id,
                examination_name,
                exam_date,
                subject_id,
                subject_name,
                subject_code,

                COUNT(*) AS total_mark_records,
                COUNT(DISTINCT student_id) AS students_evaluated,

                ROUND(AVG(percentage)::numeric, 2)
                    AS average_percentage,

                ROUND(MAX(percentage)::numeric, 2)
                    AS highest_percentage,

                ROUND(MIN(percentage)::numeric, 2)
                    AS lowest_percentage

            FROM filtered_marks

            GROUP BY
                examination_id,
                examination_name,
                exam_date,
                subject_id,
                subject_name,
                subject_code
        )

        SELECT
            es.examination_id,
            es.examination_name,
            es.exam_date,
            es.total_mark_records,
            es.students_evaluated,
            es.average_percentage,
            es.highest_percentage,
            es.lowest_percentage,

            ss.subject_id,
            ss.subject_name,
            ss.subject_code,
            ss.total_mark_records AS subject_total_mark_records,
            ss.students_evaluated AS subject_students_evaluated,
            ss.average_percentage AS subject_average_percentage,
            ss.highest_percentage AS subject_highest_percentage,
            ss.lowest_percentage AS subject_lowest_percentage

        FROM examination_summary es

        JOIN subject_summary ss
            ON ss.examination_id = es.examination_id

        ORDER BY
            es.exam_date ASC,
            es.examination_id ASC,
            ss.subject_name ASC
    """)

    with db.no_autoflush:
        rows = db.execute(
            query,
            params,
        ).mappings().all()

    examination_lookup = {}

    for row in rows:
        examination_id = row["examination_id"]

        if examination_id not in examination_lookup:
            examination_lookup[examination_id] = {
                "examination_id": examination_id,
                "examination_name": row["examination_name"],
                "exam_date": row["exam_date"],
                "total_mark_records": row["total_mark_records"],
                "students_evaluated": row["students_evaluated"],
                "average_percentage": float(
                    row["average_percentage"]
                ),
                "highest_percentage": float(
                    row["highest_percentage"]
                ),
                "lowest_percentage": float(
                    row["lowest_percentage"]
                ),
                "change_from_previous": None,
                "subjects": [],
            }

        examination_lookup[examination_id]["subjects"].append({
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
            "change_from_previous": None,
        })

    examinations = list(examination_lookup.values())

    # Calculate overall examination changes.
    for index in range(len(examinations)):
        if index > 0:
            examinations[index]["change_from_previous"] = round(
                examinations[index]["average_percentage"]
                - examinations[index - 1]["average_percentage"],
                2,
            )

    # Calculate subject changes between consecutive available exams.
    previous_subject_averages = {}

    for examination in examinations:
        for subject in examination["subjects"]:
            subject_id_value = subject["subject_id"]

            if subject_id_value in previous_subject_averages:
                subject["change_from_previous"] = round(
                    subject["average_percentage"]
                    - previous_subject_averages[subject_id_value],
                    2,
                )

            previous_subject_averages[subject_id_value] = (
                subject["average_percentage"]
            )

    return {
        "academic_period_id": academic_period_id,
        "class_id": class_id,
        "subject_id": subject_id,
        "examinations": examinations,
    }
