
import sys
import traceback
from pathlib import Path
from datetime import date

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_db, get_current_user
from app.database.connection import SessionLocal
from app.models import User
from app.models.examination import Examination


def main():
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == 1).first()

        if user is None:
            raise RuntimeError("Test user with ID 1 was not found.")

        target_date = date(2026, 12, 15)

        temporary_exam = Examination(
            institution_id=user.institution_id,
            academic_period_id=2,
            name="Temporary API Prediction Test",
            exam_date=target_date,
            start_date=target_date,
            end_date=target_date,
            description="Temporary test only.",
        )

        db.add(temporary_exam)
        db.flush()

        print(f"Temporary examination ID: {temporary_exam.id}")

        def override_get_db():
            yield db

        def override_get_current_user():
            return user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = (
            override_get_current_user
        )

        payload = {
            "student_id": 1,
            "subject_id": 1,
            "target_examination_id": temporary_exam.id,
        }

        print("\nCalling actual ML prediction HTTP endpoint...")

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ml/predictions/underperformance",
                json=payload,
            )

        print("\nHTTP STATUS:", response.status_code)
        print("\nAPI RESPONSE:")
        print(response.text)

        if response.status_code == 200:
            print("\nSUCCESS: ML prediction API test passed.")
        else:
            print("\nAPI test did not return HTTP 200.")

    except Exception:
        print("\nTEST FAILED:")
        traceback.print_exc()

    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.close()

        print("\nTemporary database changes rolled back.")
        print("Database connection closed.")


if __name__ == "__main__":
    main()
