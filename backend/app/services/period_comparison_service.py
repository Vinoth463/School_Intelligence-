
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_period_comparison(
    db: Session,
    institution_id: int,
    class_grade: str | None = None,
    class_section: str | None = None,
    class_id: int | None = None,
    subject_id: int | None = None,
):
    query = """
        SELECT
            ap.id AS academic_period_id,
            ap.name AS academic_period_name,
            ap.start_date AS period_start_date,
            s.id AS subject_id,
            s.name AS subject_name,
            s.code AS subject_code,
            COUNT(m.id) AS total_mark_records,
            COUNT(DISTINCT m.student_id) AS students_evaluated,
            COUNT(DISTINCT e.id) AS total_examinations,
            ROUND(
                AVG((m.obtained_marks / NULLIF(m.max_marks, 0)) * 100)::numeric,
                2
            ) AS average_percentage,
            ROUND(
                MAX((m.obtained_marks   / NULLIF(m.max_marks, 0)) * 100)::numeric,
                2
            ) AS highest_percentage,
            ROUND(
                MIN((m.obtained_marks / NULLIF(m.max_marks, 0)) * 100)::numeric,
                2
            ) AS lowest_percentage
        FROM marks m
        JOIN examinations e
            ON e.id = m.examination_id
        JOIN academic_periods ap
            ON ap.id = e.academic_period_id
        JOIN classes c
            ON c.id = m.class_id
        JOIN students st
            ON st.id = m.student_id
        JOIN subjects s
            ON s.id = m.subject_id
        WHERE
            ap.institution_id = :institution_id
            AND c.institution_id = :institution_id
            AND st.institution_id = :institution_id
            AND s.institution_id = :institution_id
            AND e.academic_period_id = ap.id
    """

    params = {
        "institution_id": institution_id,
    }

    if class_grade is not None:
        query += " AND c.grade = :class_grade"
        params["class_grade"] = class_grade

    if class_section is not None:
        query += " AND c.section = :class_section"
        params["class_section"] = class_section

    if subject_id is not None:
        query += " AND s.id = :subject_id"
        params["subject_id"] = subject_id

    query += """
        GROUP BY
            ap.id,
            ap.name,
            ap.start_date,
            s.id,
            s.name,
            s.code
        ORDER BY
            ap.start_date,
            ap.id,
            s.name
    """

    rows = db.execute(text(query), params).mappings().all()

    periods = {}

    for row in rows:
        period_id = row["academic_period_id"]

        if period_id not in periods:
            periods[period_id] = {
                "academic_period_id": period_id,
                "academic_period_name": row["academic_period_name"],
                "total_examinations": 0,
                "total_mark_records": 0,
                "students_evaluated": 0,
                "average_percentage": 0.0,
                "highest_percentage": 0.0,
                "lowest_percentage": 100.0,
                "change_from_previous_period": None,
                "subjects": [],
                "_weighted_total": 0.0,
            }

        period = periods[period_id]

        record_count = row["total_mark_records"]
        average = float(row["average_percentage"] or 0)

        period["_weighted_total"] += average * record_count
        period["total_mark_records"] += record_count

        period["students_evaluated"] = max(
            period["students_evaluated"],
            row["students_evaluated"],
        )

        period["total_examinations"] = max(
            period["total_examinations"],
            row["total_examinations"],
        )

        period["highest_percentage"] = max(
            period["highest_percentage"],
            float(row["highest_percentage"] or 0),
        )

        period["lowest_percentage"] = min(
            period["lowest_percentage"],
            float(row["lowest_percentage"] or 100),
        )

        period["subjects"].append({
            "subject_id": row["subject_id"],
            "subject_name": row["subject_name"],
            "subject_code": row["subject_code"],
            "total_mark_records": record_count,
            "students_evaluated": row["students_evaluated"],
            "average_percentage": average,
            "highest_percentage": float(row["highest_percentage"] or 0),
            "lowest_percentage": float(row["lowest_percentage"] or 0),
            "change_from_previous_period": None,
        })

    previous_period_average = None
    previous_subject_averages = {}

    for period in periods.values():
        total_records = period["total_mark_records"]

        period["average_percentage"] = (
            round(period["_weighted_total"] / total_records, 2)
            if total_records else 0.0
        )

        period.pop("_weighted_total")

        if previous_period_average is not None:
            period["change_from_previous_period"] = round(
                period["average_percentage"] - previous_period_average,
                2,
            )

        for subject in period["subjects"]:
            subject_id_value = subject["subject_id"]

            if subject_id_value in previous_subject_averages:
                subject["change_from_previous_period"] = round(
                    subject["average_percentage"]
                    - previous_subject_averages[subject_id_value],
                    2,
                )

            previous_subject_averages[subject_id_value] = (
                subject["average_percentage"]
            )

        previous_period_average = period["average_percentage"]

    return {
        "class_id": class_id,
        "subject_id": subject_id,
        "periods": list(periods.values()),
    }
