from pathlib import Path

from app.database.connection import SessionLocal
from app.services.import_service import import_students


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "dataset" / "generated" / "students.csv"


def main():
    file_bytes = CSV_PATH.read_bytes()

    db = SessionLocal()

    try:
        result = import_students(
            db=db,
            institution_id=1,
            uploaded_by=1,
            filename="students.csv",
            file_bytes=file_bytes,
        )

        print("\nSTUDENT IMPORT RESULT")
        for key, value in result.items():
            print(f"{key}: {value}")

    finally:
        db.close()


if __name__ == "__main__":
    main()