
import re
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.classroom import Classroom
from app.models.academic_period import AcademicPeriod
from app.models.examination import Examination
from app.models.subject import Subject
from app.models.student import Student


def resolve_question_entities(
    db: Session,
    institution_id: int,
    question: str,
) -> dict:
    """
    Resolve academic period, class, subject, student and target
    examination using institution-scoped database lookups.
    """

    result = {
        "academic_period_id": None,
        "class_id": None,
        "subject_id": None,
        "student_id": None,
        "student_name": None,
        "admission_number": None,
        "grade": None,
        "section": None,
        "subject_name": None,
        "target_examination_id": None,
        "target_examination_name": None,
        "clarification": None,
    }

    normalized_question = question.lower().strip()

    # 1. Resolve academic period.
    period_match = re.search(
        r"\b(20\d{2})\s*[-–—/]\s*(20\d{2})\b",
        normalized_question,
    )

    period_id = None

    if period_match:
        period_name = (
            f"{period_match.group(1)}-{period_match.group(2)}"
        )

        period = db.scalar(
            select(AcademicPeriod).where(
                AcademicPeriod.institution_id == institution_id,
                AcademicPeriod.name == period_name,
            )
        )

        if period is None:
            result["clarification"] = (
                f"Academic period {period_name} was not found."
            )
            return result

        period_id = period.id
        result["academic_period_id"] = period_id

    # 2. Resolve class.
    class_match = re.search(
        r"\bgrade\s*(\d+)\s*[- ]?\s*([a-z])\b",
        normalized_question,
    )

    if class_match:
        grade = f"Grade {class_match.group(1)}"
        section = class_match.group(2).upper()

        result["grade"] = grade
        result["section"] = section

        class_query = select(Classroom).where(
            Classroom.institution_id == institution_id,
            Classroom.grade.ilike(grade),
            Classroom.section.ilike(section),
        )

        if period_id is not None:
            class_query = class_query.where(
                Classroom.academic_period_id == period_id
            )

        matching_classes = db.scalars(class_query).all()

        if len(matching_classes) == 0:
            result["clarification"] = (
                f"{grade} Section {section} was not found "
                "for the selected academic period."
            )
            return result

        if len(matching_classes) > 1:
            result["clarification"] = (
                f"{grade} Section {section} exists in multiple "
                "academic periods. Please specify the academic period."
            )
            return result

        matched_class = matching_classes[0]

        result["class_id"] = matched_class.id
        result["academic_period_id"] = matched_class.academic_period_id
        period_id = matched_class.academic_period_id

    # 3. Resolve student by admission number or full name.
    students = db.scalars(
        select(Student).where(
            Student.institution_id == institution_id
        )
    ).all()

    matched_students = []

    # Prefer an exact admission-number match.
    for student in students:
        admission_number = str(student.admission_number).strip()

        if admission_number and re.search(
            rf"(?<!\w){re.escape(admission_number.lower())}(?!\w)",
            normalized_question,
        ):
            matched_students.append(student)

    # If no admission number matched, check full names.
    if not matched_students:
        for student in students:
            full_name = (
                f"{student.first_name} {student.last_name}"
            ).strip()

            normalized_name = re.sub(
                r"\s+",
                " ",
                full_name.lower(),
            )

            if normalized_name and re.search(
                rf"(?<!\w){re.escape(normalized_name)}(?!\w)",
                normalized_question,
            ):
                matched_students.append(student)

    if len(matched_students) > 1:
        result["clarification"] = (
            "Multiple students matched your question. "
            "Please provide the student's admission number."
        )
        return result

    matched_student = None

    if len(matched_students) == 1:
        matched_student = matched_students[0]

        result["student_id"] = matched_student.id
        result["student_name"] = (
            f"{matched_student.first_name} "
            f"{matched_student.last_name}"
        ).strip()
        result["admission_number"] = (
            matched_student.admission_number
        )

    # 4. Resolve subject by name or code.
    normalized_subjects = {
        subject.name.lower(): subject
        for subject in db.scalars(
            select(Subject).where(
                Subject.institution_id == institution_id
            )
        ).all()
    }

    normalized_codes = {
        subject.code.lower(): subject
        for subject in normalized_subjects.values()
    }

    matched_subjects = []

    for subject_name, subject in normalized_subjects.items():
        if re.search(
            rf"(?<!\w){re.escape(subject_name)}(?!\w)",
            normalized_question,
        ):
            matched_subjects.append(subject)

    if not matched_subjects:
        for subject_code, subject in normalized_codes.items():
            if re.search(
                rf"(?<!\w){re.escape(subject_code)}(?!\w)",
                normalized_question,
            ):
                matched_subjects.append(subject)

    if len(matched_subjects) > 1:
        result["clarification"] = (
            "Multiple subjects were identified. "
            "Please specify one subject."
        )
        return result

    if len(matched_subjects) == 1:
        result["subject_id"] = matched_subjects[0].id
        result["subject_name"] = matched_subjects[0].name

    # 5. Resolve target examination.
    # Infer the student's current academic period when appropriate.
    if matched_student is not None and period_id is None:
        student_class = db.scalar(
            select(Classroom).where(
                Classroom.id == matched_student.class_id,
                Classroom.institution_id == institution_id,
            )
        )

        if student_class is not None:
            period_id = student_class.academic_period_id
            result["academic_period_id"] = period_id

    examinations = db.scalars(
        select(Examination).where(
            Examination.institution_id == institution_id
        )
    ).all()

    asks_for_next_exam = bool(
        re.search(
            r"\b(next|upcoming|future)\s+(exam|examination)\b"
            r"|\b(exam|examination)\s+(prediction|forecast)\b",
            normalized_question,
        )
    )

    matched_examination = None

    if asks_for_next_exam:
        exam_query = select(Examination).where(
            Examination.institution_id == institution_id,
            Examination.exam_date > date.today(),
        )

        if period_id is not None:
            exam_query = exam_query.where(
                Examination.academic_period_id == period_id
            )

        future_examinations = db.scalars(
            exam_query.order_by(
                Examination.exam_date,
                Examination.id,
            )
        ).all()

        if len(future_examinations) == 1:
            matched_examination = future_examinations[0]

        elif len(future_examinations) == 0:
            result["clarification"] = (
                "No upcoming examination was found for the "
                "selected academic period. Please specify "
                "another examination or academic period."
            )
            return result

        else:
            result["clarification"] = (
                "Multiple upcoming examinations were found. "
                "Please specify the examination name or date."
            )
            return result

    else:
        for examination in examinations:
            examination_name = examination.name.strip().lower()

            if examination_name and re.search(
                rf"(?<!\w){re.escape(examination_name)}(?!\w)",
                normalized_question,
            ):
                if (
                    period_id is None
                    or examination.academic_period_id == period_id
                ):
                    if matched_examination is not None:
                        result["clarification"] = (
                            "Multiple examinations matched your question. "
                            "Please specify the academic period."
                        )
                        return result

                    matched_examination = examination

        if matched_examination is None:
            pass

    if matched_examination is not None:
        result["target_examination_id"] = matched_examination.id
        result["target_examination_name"] = matched_examination.name

    return result
