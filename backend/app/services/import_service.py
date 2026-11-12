from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path

import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models import (
    AcademicPeriod,
    Attendance,
    Classroom,
    Examination,
    ImportLog,
    ImportRejection,
    Mark,
    Student,
    Subject,
    User,
)


STUDENT_REQUIRED_COLUMNS = {
    "institution_id",
    "class_id",
    "admission_number",
    "first_name",
    "last_name",
    "admission_date",
    "status",
}

VALID_STATUSES = {
    "active",
    "inactive",
    "transferred",
    "graduated",
}

MARK_REQUIRED_COLUMNS = {
    "student_id",
    "examination_id",
    "subject_id",
    "class_id",
    "obtained_marks",
    "max_marks",
}

ATTENDANCE_REQUIRED_COLUMNS = {
    "student_id",
    "class_id",
    "subject_id",
    "session_date",
    "session_number",
    "status",
}

VALID_ATTENDANCE_STATUSES = {"present", "absent"}


def _read_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read a CSV or Excel file into a DataFrame."""

    extension = Path(filename).suffix.lower()

    if extension == ".csv":
        df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    elif extension in {".xlsx", ".xls"}:
        df = pd.read_excel(BytesIO(file_bytes))
    else:
        raise ValueError("Only CSV, XLSX and XLS files are supported.")

    df.columns = [str(column).strip().lower() for column in df.columns]

    if len(df.columns) != len(set(df.columns)):
        raise ValueError("File contains duplicate column names.")

    missing = STUDENT_REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if df.empty:
        raise ValueError("The uploaded file contains no data rows.")

    return df


def _read_marks_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read and validate the structure of a marks CSV or Excel file."""

    extension = Path(filename).suffix.lower()

    if extension == ".csv":
        df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    elif extension in {".xlsx", ".xls"}:
        df = pd.read_excel(BytesIO(file_bytes))
    else:
        raise ValueError("Only CSV, XLSX and XLS files are supported.")

    df.columns = [str(column).strip().lower() for column in df.columns]

    if len(df.columns) != len(set(df.columns)):
        raise ValueError("File contains duplicate column names.")

    missing = MARK_REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if df.empty:
        raise ValueError("The uploaded file contains no data rows.")

    return df


def _read_attendance_file(
    file_bytes: bytes,
    filename: str,
) -> pd.DataFrame:
    """Read and validate the structure of an attendance CSV or Excel file."""

    extension = Path(filename).suffix.lower()

    if extension == ".csv":
        df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    elif extension in {".xlsx", ".xls"}:
        df = pd.read_excel(BytesIO(file_bytes))
    else:
        raise ValueError("Only CSV, XLSX and XLS files are supported.")

    df.columns = [str(column).strip().lower() for column in df.columns]

    if len(df.columns) != len(set(df.columns)):
        raise ValueError("File contains duplicate column names.")

    missing = ATTENDANCE_REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if df.empty:
        raise ValueError("The uploaded file contains no data rows.")

    return df


def _is_missing(value) -> bool:
    if value is None:
        return True

    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _parse_integer(value, field_name: str) -> int:
    if _is_missing(value):
        raise ValueError(f"{field_name} is required.")

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer.")

    if not number.is_integer() or number <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")

    return int(number)


def _parse_text(value, field_name: str, max_length: int) -> str:
    if _is_missing(value):
        raise ValueError(f"{field_name} is required.")

    result = str(value).strip()

    if not result:
        raise ValueError(f"{field_name} cannot be empty.")

    if len(result) > max_length:
        raise ValueError(
            f"{field_name} exceeds {max_length} characters."
        )

    return result


def _parse_date(value) -> date:
    if _is_missing(value):
        raise ValueError("admission_date is required.")

    try:
        parsed = pd.to_datetime(value, errors="raise")
        return parsed.date()
    except (TypeError, ValueError):
        raise ValueError(
            "admission_date must be a valid date."
        )


def _parse_session_date(value) -> date:
    """Parse an attendance session date."""

    if _is_missing(value):
        raise ValueError("session_date is required.")

    try:
        parsed = pd.to_datetime(value, errors="raise")
        return parsed.date()
    except (TypeError, ValueError, OverflowError):
        raise ValueError("session_date must be a valid date.")


def _parse_decimal(value, field_name: str) -> Decimal:
    """Parse a valid NUMERIC(7, 2) value."""

    if _is_missing(value):
        raise ValueError(f"{field_name} is required.")

    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{field_name} must be a valid number.")

    if not number.is_finite():
        raise ValueError(f"{field_name} must be a finite number.")

    if number < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    if number > Decimal("99999.99"):
        raise ValueError(f"{field_name} exceeds the maximum allowed value.")

    if number.as_tuple().exponent < -2:
        raise ValueError(f"{field_name} cannot have more than 2 decimal places.")

    return number


def _json_safe(value):
    """Convert pandas/numpy values into JSON-compatible values."""

    if _is_missing(value):
        return None

    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()

    if hasattr(value, "item"):
        return value.item()

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def _prepare_student_row(row: dict) -> dict:
    student = {
        "institution_id": _parse_integer(
            row.get("institution_id"), "institution_id"
        ),
        "class_id": _parse_integer(
            row.get("class_id"), "class_id"
        ),
        "admission_number": _parse_text(
            row.get("admission_number"), "admission_number", 50
        ),
        "first_name": _parse_text(
            row.get("first_name"), "first_name", 100
        ),
        "last_name": _parse_text(
            row.get("last_name"), "last_name", 100
        ),
        "admission_date": _parse_date(
            row.get("admission_date")
        ),
        "status": _parse_text(
            row.get("status"), "status", 20
        ).lower(),
    }

    if student["status"] not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{student['status']}'. "
            f"Allowed values: {sorted(VALID_STATUSES)}."
        )

    # Optional source ID. Needed for linking the supplied
    # synthetic marks and attendance datasets.
    source_id = row.get("id")

    if not _is_missing(source_id):
        student["id"] = _parse_integer(source_id, "id")

    return student


def _prepare_mark_row(row: dict) -> dict:
    """Validate and prepare one marks row."""

    mark = {
        "student_id": _parse_integer(row.get("student_id"), "student_id"),
        "examination_id": _parse_integer(
            row.get("examination_id"), "examination_id"
        ),
        "subject_id": _parse_integer(row.get("subject_id"), "subject_id"),
        "class_id": _parse_integer(row.get("class_id"), "class_id"),
        "obtained_marks": _parse_decimal(
            row.get("obtained_marks"), "obtained_marks"
        ),
        "max_marks": _parse_decimal(row.get("max_marks"), "max_marks"),
    }

    if mark["max_marks"] <= 0:
        raise ValueError("max_marks must be greater than zero.")

    if mark["obtained_marks"] > mark["max_marks"]:
        raise ValueError("obtained_marks cannot exceed max_marks.")

    # Optional source ID, preserving the supplied synthetic dataset IDs.
    source_id = row.get("id")

    if not _is_missing(source_id):
        mark["id"] = _parse_integer(source_id, "id")

    return mark


def _prepare_attendance_row(row: dict) -> dict:
    """Validate and prepare one attendance row."""

    attendance = {
        "student_id": _parse_integer(row.get("student_id"), "student_id"),
        "class_id": _parse_integer(row.get("class_id"), "class_id"),
        "subject_id": _parse_integer(row.get("subject_id"), "subject_id"),
        "session_date": _parse_session_date(row.get("session_date")),
        "session_number": _parse_integer(
            row.get("session_number"), "session_number"
        ),
        "status": _parse_text(row.get("status"), "status", 10).lower(),
    }

    if attendance["status"] not in VALID_ATTENDANCE_STATUSES:
        raise ValueError(
            "Invalid attendance status. Allowed values: present, absent."
        )

    # Optional source ID, preserving supplied dataset IDs.
    source_id = row.get("id")

    if not _is_missing(source_id):
        attendance["id"] = _parse_integer(source_id, "id")

    return attendance


def import_students(
    db: Session,
    institution_id: int,
    uploaded_by: int,
    filename: str,
    file_bytes: bytes,
) -> dict:
    """
    Import students from CSV or Excel.

    This function manages its own database transaction.
    Valid rows are inserted; invalid rows are recorded
    in import_rejections.
    """

    if not filename or len(filename) > 255:
        raise ValueError("Invalid filename.")

    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    df = _read_file(file_bytes, filename)

    total_rows = len(df)
    accepted_rows = 0
    rejected_rows = 0

    with db.begin():
        # Confirm the institution exists.
        institution = db.scalar(
            select(User.institution_id)
            .where(User.institution_id == institution_id)
            .limit(1)
        )

        # Check institution directly through the classes table
        # and its academic periods.
        if institution is None:
            existing_institution = db.execute(
                text(
                    "SELECT id FROM institutions WHERE id = :id"
                ),
                {"id": institution_id},
            ).scalar_one_or_none()

            if existing_institution is None:
                raise ValueError("Institution does not exist.")

        # Verify the uploader belongs to this institution
        # and has an active account.
        uploader = db.scalar(
            select(User).where(
                User.id == uploaded_by,
                User.institution_id == institution_id,
                User.is_active.is_(True),
            )
        )

        if uploader is None:
            raise ValueError(
                "Uploader is not an active user of this institution."
            )

        # Load institution-specific classes.
        class_rows = db.execute(
            select(Classroom, AcademicPeriod)
            .join(
                AcademicPeriod,
                Classroom.academic_period_id == AcademicPeriod.id,
            )
            .where(Classroom.institution_id == institution_id)
        ).all()

        classes = {
            classroom.id: classroom
            for classroom, _ in class_rows
        }

        # Existing admission numbers and student IDs.
        existing_admissions = set(
            db.scalars(
                select(Student.admission_number).where(
                    Student.institution_id == institution_id
                )
            ).all()
        )

        existing_ids = set(
            db.scalars(select(Student.id)).all()
        )

        seen_admissions = {
            value.casefold() for value in existing_admissions
        }

        seen_ids = set(existing_ids)

        valid_students = []
        rejection_records = []

        import_log = ImportLog(
            institution_id=institution_id,
            uploaded_by=uploaded_by,
            file_name=filename,
            import_type="students",
            status="processing",
            total_rows=total_rows,
            accepted_rows=0,
            rejected_rows=0,
        )

        db.add(import_log)
        db.flush()

        # Validate each source row independently.
        for index, series in df.iterrows():
            row_number = index + 2
            raw_row = series.to_dict()

            try:
                student = _prepare_student_row(raw_row)

                if student["institution_id"] != institution_id:
                    raise ValueError(
                        "Student institution_id does not match "
                        "the selected institution."
                    )

                classroom = classes.get(student["class_id"])

                if classroom is None:
                    raise ValueError(
                        "class_id does not exist in this institution."
                    )

                admission_key = student[
                    "admission_number"
                ].casefold()

                if admission_key in seen_admissions:
                    raise ValueError(
                        "Duplicate admission_number."
                    )

                if "id" in student:
                    if student["id"] in seen_ids:
                        raise ValueError(
                            "Student ID already exists."
                        )

                    seen_ids.add(student["id"])

                seen_admissions.add(admission_key)
                valid_students.append(student)
                accepted_rows += 1

            except ValueError as exc:
                rejected_rows += 1

                rejection_records.append(
                    ImportRejection(
                        import_log_id=import_log.id,
                        row_number=row_number,
                        rejection_reason=str(exc),
                        raw_data={
                            str(key): _json_safe(value)
                            for key, value in raw_row.items()
                        },
                    )
                )

        # Insert validated rows.
        db.add_all(
            [Student(**student) for student in valid_students]
        )

        # Store rejected rows and their reasons.
        db.add_all(rejection_records)

        db.flush()

        # Update the ID sequence when explicit source IDs
        # have been supplied.
        if any("id" in student for student in valid_students):
            db.execute(
                text(
                    """
                    SELECT setval(
                        pg_get_serial_sequence('students', 'id'),
                        COALESCE(MAX(id), 1),
                        MAX(id) IS NOT NULL
                    )
                    FROM students
                    """
                )
            )

        import_log.accepted_rows = accepted_rows
        import_log.rejected_rows = rejected_rows
        import_log.status = "completed"
        import_log.completed_at = datetime.now(timezone.utc)

        import_id = import_log.id

    return {
        "import_id": import_id,
        "file_name": filename,
        "import_type": "students",
        "total_rows": total_rows,
        "accepted_rows": accepted_rows,
        "rejected_rows": rejected_rows,
        "status": "completed",
    }


def import_marks(
    db: Session,
    institution_id: int,
    uploaded_by: int,
    filename: str,
    file_bytes: bytes,
) -> dict:
    """
    Import examination marks from CSV or Excel.

    Valid rows are inserted.
    Invalid rows are recorded in import_rejections.
    The function manages its own transaction.
    """

    if not filename or len(filename) > 255:
        raise ValueError("Invalid filename.")

    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    df = _read_marks_file(file_bytes, filename)

    total_rows = len(df)
    accepted_rows = 0
    rejected_rows = 0

    with db.begin():

        # Verify institution exists.
        institution_exists = db.execute(
            text("SELECT id FROM institutions WHERE id = :id"),
            {"id": institution_id},
        ).scalar_one_or_none()

        if institution_exists is None:
            raise ValueError("Institution does not exist.")

        # Verify uploader belongs to the institution.
        uploader = db.scalar(
            select(User).where(
                User.id == uploaded_by,
                User.institution_id == institution_id,
                User.is_active.is_(True),
            )
        )

        if uploader is None:
            raise ValueError(
                "Uploader is not an active user of this institution."
            )

        # Load institution-specific reference records.
        students = {
            student.id: student
            for student in db.scalars(
                select(Student).where(
                    Student.institution_id == institution_id
                )
            ).all()
        }

        examinations = {
            exam.id: exam
            for exam in db.scalars(
                select(Examination).where(
                    Examination.institution_id == institution_id
                )
            ).all()
        }

        subjects = {
            subject.id: subject
            for subject in db.scalars(
                select(Subject).where(
                    Subject.institution_id == institution_id
                )
            ).all()
        }

        classes = {
            classroom.id: classroom
            for classroom in db.scalars(
                select(Classroom).where(
                    Classroom.institution_id == institution_id
                )
            ).all()
        }

        # Find existing marks for this institution.
        existing_keys = set(
            db.execute(
                select(
                    Mark.student_id,
                    Mark.examination_id,
                    Mark.subject_id,
                )
                .join(Student, Mark.student_id == Student.id)
                .where(Student.institution_id == institution_id)
            ).all()
        )

        # Mark IDs are globally unique.
        existing_ids = set(
            db.scalars(select(Mark.id)).all()
        )

        seen_keys = set(existing_keys)
        seen_ids = set(existing_ids)

        valid_marks = []
        rejection_records = []

        # Create import tracking record.
        import_log = ImportLog(
            institution_id=institution_id,
            uploaded_by=uploaded_by,
            file_name=filename,
            import_type="marks",
            status="processing",
            total_rows=total_rows,
            accepted_rows=0,
            rejected_rows=0,
        )

        db.add(import_log)
        db.flush()

        # Validate every row independently.
        for index, series in df.iterrows():

            row_number = index + 2
            raw_row = series.to_dict()

            try:
                mark = _prepare_mark_row(raw_row)

                student = students.get(mark["student_id"])
                examination = examinations.get(mark["examination_id"])
                subject = subjects.get(mark["subject_id"])
                classroom = classes.get(mark["class_id"])

                if student is None:
                    raise ValueError(
                        "student_id does not exist in this institution."
                    )

                if examination is None:
                    raise ValueError(
                        "examination_id does not exist in this institution."
                    )

                if subject is None:
                    raise ValueError(
                        "subject_id does not exist in this institution."
                    )

                if classroom is None:
                    raise ValueError(
                        "class_id does not exist in this institution."
                    )

                # A student cannot have marks before admission.
                if examination.exam_date < student.admission_date:
                    raise ValueError(
                        "Examination date is before the student's admission date."
                    )

                # Historical class must belong to the exam's academic period.
                if (
                    classroom.academic_period_id
                    != examination.academic_period_id
                ):
                    raise ValueError(
                        "Class and examination belong to different academic periods."
                    )

                # Prevent duplicate student/exam/subject combinations.
                duplicate_key = (
                    mark["student_id"],
                    mark["examination_id"],
                    mark["subject_id"],
                )

                if duplicate_key in seen_keys:
                    raise ValueError(
                        "Duplicate marks record for this student, examination and subject."
                    )

                # Validate optional source ID.
                if "id" in mark:

                    if mark["id"] in seen_ids:
                        raise ValueError("Mark ID already exists.")

                    seen_ids.add(mark["id"])

                seen_keys.add(duplicate_key)

                valid_marks.append(mark)
                accepted_rows += 1

            except ValueError as exc:

                rejected_rows += 1

                rejection_records.append(
                    ImportRejection(
                        import_log_id=import_log.id,
                        row_number=row_number,
                        rejection_reason=str(exc),
                        raw_data={
                            str(key): _json_safe(value)
                            for key, value in raw_row.items()
                        },
                    )
                )

        # Insert accepted marks.
        db.add_all(
            [Mark(**mark) for mark in valid_marks]
        )

        # Save rejected rows and their reasons.
        db.add_all(rejection_records)

        db.flush()

        # Reset the PostgreSQL ID sequence when source IDs are provided.
        if any("id" in mark for mark in valid_marks):

            db.execute(
                text(
                    """
                    SELECT setval(
                        pg_get_serial_sequence('marks', 'id'),
                        COALESCE(MAX(id), 1),
                        MAX(id) IS NOT NULL
                    )
                    FROM marks
                    """
                )
            )

        # Complete import tracking.
        import_log.accepted_rows = accepted_rows
        import_log.rejected_rows = rejected_rows
        import_log.status = "completed"
        import_log.completed_at = datetime.now(timezone.utc)

        import_id = import_log.id

    return {
        "import_id": import_id,
        "file_name": filename,
        "import_type": "marks",
        "total_rows": total_rows,
        "accepted_rows": accepted_rows,
        "rejected_rows": rejected_rows,
        "status": "completed",
    }


def import_attendance(
    db: Session,
    institution_id: int,
    uploaded_by: int,
    filename: str,
    file_bytes: bytes,
) -> dict:
    """
    Import attendance from CSV or Excel.

    Valid rows are inserted.
    Invalid rows are recorded in import_rejections.
    """

    if not filename or len(filename) > 255:
        raise ValueError("Invalid filename.")

    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    df = _read_attendance_file(file_bytes, filename)

    total_rows = len(df)
    accepted_rows = 0
    rejected_rows = 0

    with db.begin():

        # Verify institution exists.
        institution_exists = db.execute(
            text("SELECT id FROM institutions WHERE id = :id"),
            {"id": institution_id},
        ).scalar_one_or_none()

        if institution_exists is None:
            raise ValueError("Institution does not exist.")

        # Verify uploader belongs to this institution.
        uploader = db.scalar(
            select(User).where(
                User.id == uploaded_by,
                User.institution_id == institution_id,
                User.is_active.is_(True),
            )
        )

        if uploader is None:
            raise ValueError(
                "Uploader is not an active user of this institution."
            )

        # Load institution-specific students.
        students = {
            student.id: student
            for student in db.scalars(
                select(Student).where(
                    Student.institution_id == institution_id
                )
            ).all()
        }

        # Load institution-specific subjects.
        subjects = {
            subject.id: subject
            for subject in db.scalars(
                select(Subject).where(
                    Subject.institution_id == institution_id
                )
            ).all()
        }

        # Load academic periods and classes for this institution.
        class_rows = db.execute(
            select(Classroom, AcademicPeriod)
            .join(
                AcademicPeriod,
                Classroom.academic_period_id == AcademicPeriod.id,
            )
            .where(
                Classroom.institution_id == institution_id,
                AcademicPeriod.institution_id == institution_id,
            )
        ).all()

        classes = {
            classroom.id: (classroom, period)
            for classroom, period in class_rows
        }

        # Load existing attendance keys for this institution.
        existing_keys = set(
            db.execute(
                select(
                    Attendance.student_id,
                    Attendance.subject_id,
                    Attendance.session_date,
                    Attendance.session_number,
                )
                .join(
                    Student,
                    Attendance.student_id == Student.id,
                )
                .where(Student.institution_id == institution_id)
            ).all()
        )

        # Attendance IDs are globally unique.
        existing_ids = set(
            db.scalars(select(Attendance.id)).all()
        )

        seen_keys = set(existing_keys)
        seen_ids = set(existing_ids)

        valid_attendance = []
        rejection_records = []

        # Create import tracking record.
        import_log = ImportLog(
            institution_id=institution_id,
            uploaded_by=uploaded_by,
            file_name=filename,
            import_type="attendance",
            status="processing",
            total_rows=total_rows,
            accepted_rows=0,
            rejected_rows=0,
        )

        db.add(import_log)
        db.flush()

        # Validate every source row independently.
        for index, series in df.iterrows():

            row_number = index + 2
            raw_row = series.to_dict()

            try:
                attendance = _prepare_attendance_row(raw_row)

                student = students.get(attendance["student_id"])
                subject = subjects.get(attendance["subject_id"])
                class_info = classes.get(attendance["class_id"])

                if student is None:
                    raise ValueError(
                        "student_id does not exist in this institution."
                    )

                if subject is None:
                    raise ValueError(
                        "subject_id does not exist in this institution."
                    )

                if class_info is None:
                    raise ValueError(
                        "class_id does not exist in this institution."
                    )

                classroom, academic_period = class_info
                session_date = attendance["session_date"]

                # Attendance cannot precede student admission.
                if session_date < student.admission_date:
                    raise ValueError(
                        "Session date is before the student's admission date."
                    )

                # Session date must be inside the class academic period.
                if not (
                    academic_period.start_date
                    <= session_date
                    <= academic_period.end_date
                ):
                    raise ValueError(
                        "Session date is outside the class academic period."
                    )

                # Prevent duplicate attendance sessions.
                duplicate_key = (
                    attendance["student_id"],
                    attendance["subject_id"],
                    attendance["session_date"],
                    attendance["session_number"],
                )

                if duplicate_key in seen_keys:
                    raise ValueError(
                        "Duplicate attendance record for this student, "
                        "subject, date and session number."
                    )

                # Validate optional source ID.
                if "id" in attendance:

                    if attendance["id"] in seen_ids:
                        raise ValueError("Attendance ID already exists.")

                    seen_ids.add(attendance["id"])

                seen_keys.add(duplicate_key)

                valid_attendance.append(attendance)
                accepted_rows += 1

            except ValueError as exc:

                rejected_rows += 1

                rejection_records.append(
                    ImportRejection(
                        import_log_id=import_log.id,
                        row_number=row_number,
                        rejection_reason=str(exc),
                        raw_data={
                            str(key): _json_safe(value)
                            for key, value in raw_row.items()
                        },
                    )
                )

        # Insert accepted attendance records.
        db.add_all(
            [
                Attendance(**record)
                for record in valid_attendance
            ]
        )

        # Save rejected rows and their reasons.
        db.add_all(rejection_records)

        db.flush()

        # Reset PostgreSQL ID sequence when source IDs are provided.
        if any("id" in record for record in valid_attendance):

            db.execute(
                text(
                    """
                    SELECT setval(
                        pg_get_serial_sequence('attendance', 'id'),
                        COALESCE(MAX(id), 1),
                        MAX(id) IS NOT NULL
                    )
                    FROM attendance
                    """
                )
            )

        import_log.accepted_rows = accepted_rows
        import_log.rejected_rows = rejected_rows
        import_log.status = "completed"
        import_log.completed_at = datetime.now(timezone.utc)

        import_id = import_log.id

    return {
        "import_id": import_id,
        "file_name": filename,
        "import_type": "attendance",
        "total_rows": total_rows,
        "accepted_rows": accepted_rows,
        "rejected_rows": rejected_rows,
        "status": "completed",
    }