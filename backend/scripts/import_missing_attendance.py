
from io import BytesIO
from pathlib import Path

import pandas as pd
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models import Attendance
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

    # Read the corrected attendance CSV.
    df = pd.read_csv(CSV_PATH)

    print("SOURCE CSV ROWS:", len(df))

    # Step 1: Find existing attendance IDs.
    # Use a separate session so the import session
    # starts with a clean transaction.
    check_db = SessionLocal()

    try:
        existing_ids = set(
            check_db.execute(
                select(Attendance.id)
            ).scalars().all()
        )
    finally:
        check_db.close()

    print("EXISTING DATABASE RECORDS:", len(existing_ids))

    # Step 2: Keep only records not already in PostgreSQL.
    missing_df = df[~df["id"].isin(existing_ids)].copy()

    print("MISSING RECORDS TO IMPORT:", len(missing_df))

    if missing_df.empty:
        print("No missing attendance records found.")
        return

    # Expected from our previous import:
    # 51,756 accepted + 1,044 rejected.
    if len(missing_df) != 1044:
        raise RuntimeError(
            f"Expected 1044 missing records, "
            f"but found {len(missing_df)}. "
            "Import stopped for safety."
        )

    # Step 3: Convert only missing rows into CSV bytes.
    csv_buffer = BytesIO()
    missing_df.to_csv(csv_buffer, index=False)
    file_bytes = csv_buffer.getvalue()

    # Step 4: Import missing records.
    db = SessionLocal()

    try:
        result = import_attendance(
            db=db,
            institution_id=1,
            uploaded_by=1,
            filename="attendance_missing_1044.csv",
            file_bytes=file_bytes,
        )

        print("\nMISSING ATTENDANCE IMPORT RESULT")

        for key, value in result.items():
            print(f"{key}: {value}")

    finally:
        db.close()

    # Step 5: Independently verify final database count.
    verify_db = SessionLocal()

    try:
        final_count = len(
            verify_db.execute(
                select(Attendance.id)
            ).scalars().all()
        )

        print("\nFINAL DATABASE VERIFICATION")
        print("Total attendance records:", final_count)
        print("Expected attendance records:", 52800)

        if final_count == 52800:
            print("SUCCESS: Attendance dataset is complete.")
        else:
            print("WARNING: Attendance count does not match.")

    finally:
        verify_db.close()


if __name__ == "__main__":
    main()
