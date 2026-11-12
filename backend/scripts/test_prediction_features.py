
import sys
import traceback
from pathlib import Path
from datetime import date

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.database.connection import SessionLocal
from app.models.examination import Examination
from app.ml.feature_service import build_prediction_features
from app.ml.prediction_service import predict_underperformance


def main():
    db = SessionLocal()

    try:
        print("=" * 65)
        print("SCHOOL INTELLIGENCE - FULL ML PREDICTION TEST")
        print("=" * 65)

        # Create a temporary examination inside this transaction.
        # The transaction will be rolled back at the end.
        target_date = date(2026, 12, 15)

        temporary_exam = Examination(
            institution_id=1,
            academic_period_id=2,
            name="Temporary ML Prediction Test",
            exam_date=target_date,
            start_date=target_date,
            end_date=target_date,
            description="Temporary examination for ML testing only.",
        )

        db.add(temporary_exam)
        db.flush()

        print(f"\nTemporary examination ID: {temporary_exam.id}")
        print(f"Temporary examination date: {target_date}")

        print("\nSTEP 1: BUILDING DATABASE FEATURES")

        features = build_prediction_features(
            db=db,
            institution_id=1,
            student_id=1,
            subject_id=1,
            target_examination_id=temporary_exam.id,
        )

        print("\nGenerated features:")
        for name, value in features.items():
            print(f"{name}: {value}")

        print("\nSTEP 2: RUNNING RANDOM FOREST PREDICTION")

        result = predict_underperformance(features)

        print("\nPrediction result:")
        for name, value in result.items():
            print(f"{name}: {value}")

        print("\nSUCCESS: Database feature generation and ML inference completed.")

    except Exception:
        print("\nTEST FAILED:")
        traceback.print_exc()

    finally:
        # Discard the temporary examination and any other transaction changes.
        db.rollback()
        db.close()

        print("\nTemporary database changes rolled back.")
        print("Database connection closed.")


if __name__ == "__main__":
    main()
