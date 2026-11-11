
import csv
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import func, select, text

# Make the project root available for imports.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database.connection import SessionLocal
from app.models import (
    Institution,
    AcademicPeriod,
    Classroom,
    Subject,
    Examination,
)


DATA_DIR = PROJECT_ROOT / "dataset" / "generated"

FILES = {
    "institutions": "institutions.csv",
    "academic_periods": "academic_periods.csv",
    "classes": "classes.csv",
    "subjects": "subjects.csv",
    "examinations": "examinations.csv",
}

MODELS = {
    "institutions": Institution,
    "academic_periods": AcademicPeriod,
    "classes": Classroom,
    "subjects": Subject,
    "examinations": Examination,
}


def parse_int(value, field, row_number):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"Row {row_number}: '{field}' must be an integer."
        )


def parse_date(value, field, row_number):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"Row {row_number}: '{field}' must use YYYY-MM-DD."
        )


def parse_bool(value, field, row_number):
    normalized = str(value).strip().lower()

    if normalized == "true":
        return True

    if normalized == "false":
        return False

    raise ValueError(
        f"Row {row_number}: '{field}' must be true or false."
    )


def load_csv(table_name, filename, required_columns):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    records = []

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"{filename} is empty.")

        missing = set(required_columns) - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"{filename}: missing columns {sorted(missing)}"
            )

        for row_number, row in enumerate(reader, start=2):
            record = {
                key: (value.strip() if value is not None else "")
                for key, value in row.items()
                if key is not None
            }

            if not any(record.values()):
                continue

            records.append(record)

    if not records:
        raise ValueError(f"{filename} contains no data rows.")

    print(f"Loaded {len(records)} rows from {filename}")

    return records


def ensure_unique(records, fields, label):
    seen = set()

    for record in records:
        key = tuple(record[field] for field in fields)

        if key in seen:
            raise ValueError(
                f"Duplicate {label}: {key}"
            )

        seen.add(key)


def validate_and_prepare():
    raw = {}

    columns = {
        "institutions": [
            "id", "name", "code", "address", "created_at"
        ],
        "academic_periods": [
            "id", "institution_id", "name", "start_date",
            "end_date", "is_active", "created_at"
        ],
        "classes": [
            "id", "institution_id", "academic_period_id",
            "grade", "section", "created_at"
        ],
        "subjects": [
            "id", "institution_id", "name", "code",
            "description", "created_at"
        ],
        "examinations": [
            "id", "institution_id", "academic_period_id",
            "name", "exam_date", "start_date", "end_date",
            "description", "created_at"
        ],
    }

    for table_name, filename in FILES.items():
        raw[table_name] = load_csv(
            table_name,
            filename,
            columns[table_name],
        )

    # Convert CSV strings into database-compatible Python values.
    institutions = []

    for i, row in enumerate(raw["institutions"], start=2):
        name = row["name"]
        code = row["code"]

        if not name or not code:
            raise ValueError(f"institutions.csv row {i}: name/code required.")

        institutions.append({
            "id": parse_int(row["id"], "id", i),
            "name": name,
            "code": code,
            "address": row["address"] or None,
        })

    periods = []

    for i, row in enumerate(raw["academic_periods"], start=2):
        start = parse_date(row["start_date"], "start_date", i)
        end = parse_date(row["end_date"], "end_date", i)

        if end <= start:
            raise ValueError(f"academic_periods.csv row {i}: invalid date range.")

        if not row["name"]:
            raise ValueError(f"academic_periods.csv row {i}: name required.")

        periods.append({
            "id": parse_int(row["id"], "id", i),
            "institution_id": parse_int(row["institution_id"], "institution_id", i),
            "name": row["name"],
            "start_date": start,
            "end_date": end,
            "is_active": parse_bool(row["is_active"], "is_active", i),
        })

    classes = []

    for i, row in enumerate(raw["classes"], start=2):
        if not row["grade"] or not row["section"]:
            raise ValueError(f"classes.csv row {i}: grade and section required.")

        classes.append({
            "id": parse_int(row["id"], "id", i),
            "institution_id": parse_int(row["institution_id"], "institution_id", i),
            "academic_period_id": parse_int(row["academic_period_id"], "academic_period_id", i),
            "grade": row["grade"],
            "section": row["section"],
        })

    subjects = []

    for i, row in enumerate(raw["subjects"], start=2):
        if not row["name"] or not row["code"]:
            raise ValueError(f"subjects.csv row {i}: name and code required.")

        subjects.append({
            "id": parse_int(row["id"], "id", i),
            "institution_id": parse_int(row["institution_id"], "institution_id", i),
            "name": row["name"],
            "code": row["code"],
            "description": row["description"] or None,
        })

    examinations = []

    for i, row in enumerate(raw["examinations"], start=2):
        exam_date = parse_date(row["exam_date"], "exam_date", i)
        start = parse_date(row["start_date"], "start_date", i)
        end = parse_date(row["end_date"], "end_date", i)

        if not row["name"]:
            raise ValueError(f"examinations.csv row {i}: name required.")

        if not start <= exam_date <= end:
            raise ValueError(f"examinations.csv row {i}: exam date outside exam range.")

        examinations.append({
            "id": parse_int(row["id"], "id", i),
            "institution_id": parse_int(row["institution_id"], "institution_id", i),
            "academic_period_id": parse_int(row["academic_period_id"], "academic_period_id", i),
            "name": row["name"],
            "exam_date": exam_date,
            "start_date": start,
            "end_date": end,
            "description": row["description"] or None,
        })

    # Check primary-key uniqueness.
    for table_name, records in [
        ("institutions", institutions),
        ("academic_periods", periods),
        ("classes", classes),
        ("subjects", subjects),
        ("examinations", examinations),
    ]:
        ensure_unique(records, ["id"], f"{table_name} ID")

    # Check business-level uniqueness.
    ensure_unique(institutions, ["name"], "institution name")
    ensure_unique(institutions, ["code"], "institution code")
    ensure_unique(periods, ["institution_id", "name"], "academic period")
    ensure_unique(classes, ["institution_id", "academic_period_id", "grade", "section"], "class")
    ensure_unique(subjects, ["institution_id", "code"], "subject code")
    ensure_unique(examinations, ["institution_id", "academic_period_id", "name"], "examination")

    institution_ids = {r["id"] for r in institutions}
    period_map = {r["id"]: r for r in periods}

    # Validate academic-period institution references.
    for row in periods:
        if row["institution_id"] not in institution_ids:
            raise ValueError(
                f"Academic period {row['id']}: institution does not exist."
            )

    # Validate class references and institution consistency.
    for row in classes:
        period = period_map.get(row["academic_period_id"])

        if row["institution_id"] not in institution_ids:
            raise ValueError(f"Class {row['id']}: institution does not exist.")

        if period is None:
            raise ValueError(f"Class {row['id']}: academic period does not exist.")

        if period["institution_id"] != row["institution_id"]:
            raise ValueError(f"Class {row['id']}: institution/period mismatch.")

    # Validate subject references.
    for row in subjects:
        if row["institution_id"] not in institution_ids:
            raise ValueError(f"Subject {row['id']}: institution does not exist.")

    # Validate examination references and dates.
    for row in examinations:
        period = period_map.get(row["academic_period_id"])

        if row["institution_id"] not in institution_ids:
            raise ValueError(f"Examination {row['id']}: institution does not exist.")

        if period is None:
            raise ValueError(f"Examination {row['id']}: academic period does not exist.")

        if period["institution_id"] != row["institution_id"]:
            raise ValueError(f"Examination {row['id']}: institution/period mismatch.")

        if not period["start_date"] <= row["exam_date"] <= period["end_date"]:
            raise ValueError(
                f"Examination {row['id']}: exam date outside academic period."
            )

    return {
        "institutions": institutions,
        "academic_periods": periods,
        "classes": classes,
        "subjects": subjects,
        "examinations": examinations,
    }


def import_foundation_data():
    data = validate_and_prepare()

    print("\nAll CSV validation checks passed.")

    with SessionLocal.begin() as db:
        # Never silently mix bootstrap data with existing records.
        for table_name, model in MODELS.items():
            count = db.scalar(
                select(func.count()).select_from(model)
            )

            if count:
                raise RuntimeError(
                    f"Table '{table_name}' already contains {count} records. "
                    "Bootstrap import stopped without modifying data."
                )

        # Insert in foreign-key dependency order.
        import_order = [
            "institutions",
            "academic_periods",
            "classes",
            "subjects",
            "examinations",
        ]

        for table_name in import_order:
            model = MODELS[table_name]
            records = data[table_name]

            db.add_all([model(**record) for record in records])
            db.flush()

            print(f"Inserted {len(records)} rows into {table_name}.")

        # CSV IDs were inserted explicitly. Reset PostgreSQL sequences
        # so future automatically generated IDs do not collide.
        for table_name in import_order:
            db.execute(text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', 'id'),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                )
                FROM {table_name}
                """
            ))

    print("\nBootstrap import completed successfully.")
    print("Imported foundational tables:")

    for table_name in import_order:
        print(f"  {table_name}: {len(data[table_name])} rows")


if __name__ == "__main__":
    try:
        import_foundation_data()
    except Exception as exc:
        print(f"\nBOOTSTRAP IMPORT FAILED: {exc}")
        print("The database transaction was rolled back.")
        raise SystemExit(1)
