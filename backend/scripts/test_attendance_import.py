from pathlib import Path

from app.database.connection import SessionLocal
from app.services.import_service import import_attendance


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "generated"
    / "attendance.csv"
)


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Attendance CSV not found: {CSV_PATH}"
        )

    file_bytes = CSV_PATH.read_bytes()
    db = SessionLocal()

    try:
        result = import_attendance(
            db=db,
            institution_id=1,
            uploaded_by=1,
            filename="attendance.csv",
            file_bytes=file_bytes,
        )

        print("\nATTENDANCE IMPORT RESULT")

        for key, value in result.items():
            print(f"{key}: {value}")

    finally:
        db.close()


if __name__ == "__main__":
    main()