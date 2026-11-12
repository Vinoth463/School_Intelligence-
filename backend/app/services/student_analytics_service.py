
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_student_performance(
    db: Session,
    institution_id: int,
    student_id: int,
    academic_period_id: int | None = None,
) -> dict | None:

    conditions = [
        "s.id = :student_id",
        "s.institution_id = :institution_id",
        "e.institution_id = :institution_id",
        "sub.institution_id = :institution_id",
        "c.institution_id = :institution_id",
        "e.academic_period_id = c.academic_period_id",
    ]

    params = {
        "student_id": student_id,
        "institution_id": institution_id,
    }

    if academic_period_id is not None:
        conditions.append(
            "e.academic_period_id = :academic_period_id"
        )
        params["academic_period_id"] = academic_period_id

    where_clause = " AND ".join(conditions)

    query = text(f"""
        SELECT
            s.id AS student_id,
            s.admission_number,
            s.first_name,
            s.last_name,

            e.id AS examination_id,
            e.name AS examination_name,
            e.academic_period_id,
            e.exam_date,

            sub.id AS subject_id,
            sub.name AS subject_name,
            sub.code AS subject_code,

            m.obtained_marks,
            m.max_marks,

            ROUND(
                (
                    m.obtained_marks
                    / NULLIF(m.max_marks, 0)
                )::numeric * 100,
                2
            ) AS percentage

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

        ORDER BY
            e.exam_date ASC,
            sub.name ASC
    """)

    with db.no_autoflush:
        rows = db.execute(query, params).mappings().all()

    if not rows:
        return None

    student = {
        "student_id": rows[0]["student_id"],
        "admission_number": rows[0]["admission_number"],
        "first_name": rows[0]["first_name"],
        "last_name": rows[0]["last_name"],
        "examinations": [],
    }

    exam_lookup = {}

    for row in rows:
        exam_id = row["examination_id"]

        if exam_id not in exam_lookup:
            exam_data = {
                "examination_id": exam_id,
                "examination_name": row["examination_name"],
                "academic_period_id": row["academic_period_id"],
                "exam_date": row["exam_date"],
                "total_obtained_marks": 0.0,
                "total_max_marks": 0.0,
                "overall_percentage": 0.0,
                "subjects": [],
            }

            exam_lookup[exam_id] = exam_data
            student["examinations"].append(exam_data)

        exam_data = exam_lookup[exam_id]

        obtained = float(row["obtained_marks"])
        maximum = float(row["max_marks"])

        exam_data["total_obtained_marks"] += obtained
        exam_data["total_max_marks"] += maximum

        exam_data["subjects"].append({
            "subject_id": row["subject_id"],
            "subject_name": row["subject_name"],
            "subject_code": row["subject_code"],
            "obtained_marks": obtained,
            "max_marks": maximum,
            "percentage": float(row["percentage"]),
        })

    for exam_data in student["examinations"]:
        total_max = exam_data["total_max_marks"]

        if total_max > 0:
            exam_data["overall_percentage"] = round(
                exam_data["total_obtained_marks"]
                / total_max * 100,
                2,
            )

        exam_data["total_obtained_marks"] = round(
            exam_data["total_obtained_marks"], 2
        )
        exam_data["total_max_marks"] = round(
            exam_data["total_max_marks"], 2
        )

    percentages = [
        exam["overall_percentage"]
        for exam in student["examinations"]
    ]

    student["performance_trend"] = []

    for index, exam in enumerate(student["examinations"]):
        change = None

        if index > 0:
            change = round(
                percentages[index] - percentages[index - 1],
                2,
            )

        student["performance_trend"].append({
            "examination_id": exam["examination_id"],
            "examination_name": exam["examination_name"],
            "overall_percentage": percentages[index],
            "change_from_previous": change,
        })

    return student
