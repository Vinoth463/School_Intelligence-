
import sys
from pathlib import Path

# Add the backend root directory to Python's import path.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database.connection import SessionLocal
from app.services.declining_performance_service import (
    get_declining_performance,
)

db = SessionLocal()

try:
    for period_id in [1, 2]:

        print("\n" + "=" * 65)
        print(f"DECLINING PERFORMANCE - PERIOD {period_id}")
        print("=" * 65)

        results = get_declining_performance(
            db=db,
            institution_id=1,
            academic_period_id=period_id,
            decline_threshold=0.0,
        )

        print("\nTotal declining records:", len(results))

        for row in results[:15]:
            print(
                f'{row["admission_number"]} | '
                f'{row["previous_examination_name"]} -> '
                f'{row["examination_name"]} | '
                f'{row["previous_percentage"]}% -> '
                f'{row["current_percentage"]}% | '
                f'Change: {row["percentage_change"]} percentage points | '
                f'Status: {row["performance_status"]}'
            )

        assert all(
            row["current_percentage"] < row["previous_percentage"]
            for row in results
        ), "A non-declining record was returned"

        assert all(
            row["performance_status"] == "declining"
            for row in results
        ), "Unexpected performance status"

        print("\nVALIDATION: PASSED")

finally:
    db.close()
    print("\nDatabase session closed.")
