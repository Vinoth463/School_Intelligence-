
from app.database.connection import SessionLocal
from app.services.analytics_service import get_dashboard_overview


def main():
    db = SessionLocal()

    try:
        print("\nDASHBOARD ANALYTICS TEST")
        print("=" * 45)

        result = get_dashboard_overview(
            db=db,
            institution_id=1,
        )

        for key, value in result.items():
            print(f"{key}: {value}")

        print("\nACADEMIC PERIOD 1")
        print("-" * 45)

        period_1 = get_dashboard_overview(
            db=db,
            institution_id=1,
            academic_period_id=1,
        )

        for key, value in period_1.items():
            print(f"{key}: {value}")

        print("\nACADEMIC PERIOD 2")
        print("-" * 45)

        period_2 = get_dashboard_overview(
            db=db,
            institution_id=1,
            academic_period_id=2,
        )

        for key, value in period_2.items():
            print(f"{key}: {value}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
