
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database.connection import SessionLocal
from app.services.declining_performance_service import (
    get_subject_declines,
)

db = SessionLocal()

try:
    for period_id in [1, 2]:

        print("\n" + "=" * 65)
        print(f"SUBJECT-WISE DECLINES - PERIOD {period_id}")
        print("=" * 65)

        results = get_subject_declines(
            db=db,
            institution_id=1,
            academic_period_id=period_id,
        )

        print("\nTotal subject decline records:", len(results))

        for row in results[:15]:
            print(
                f'{row["admission_number"]} | '
                f'{row["subject_name"]} | '
                f'{row["previous_examination_name"]} -> '
                f'{row["examination_name"]} | '
                f'{row["previous_percentage"]}% -> '
                f'{row["current_percentage"]}% | '
                f'Change: {row["percentage_change"]} percentage points'
            )

        assert all(
            row["current_percentage"] < row["previous_percentage"]
            for row in results
        ), "A non-declining subject record was returned"

        print("\nVALIDATION: PASSED")

finally:
    db.close()
    print("\nDatabase session closed.")
