
from sqlalchemy import text
from app.database.connection import engine


def main():
    queries = {
        "institutions": "SELECT COUNT(*) FROM institutions",
        "academic_periods": "SELECT COUNT(*) FROM academic_periods",
        "classes": "SELECT COUNT(*) FROM classes",
        "students": "SELECT COUNT(*) FROM students",
        "subjects": "SELECT COUNT(*) FROM subjects",
        "examinations": "SELECT COUNT(*) FROM examinations",
        "marks": "SELECT COUNT(*) FROM marks",
        "attendance": "SELECT COUNT(*) FROM attendance",
        "users": "SELECT COUNT(*) FROM users",
        "import_logs": "SELECT COUNT(*) FROM import_logs",
        "import_rejections": "SELECT COUNT(*) FROM import_rejections",
    }

    with engine.connect() as connection:

        print("\nSCHOOL INTELLIGENCE DATABASE VERIFICATION")
        print("=" * 50)

        for table, query in queries.items():
            count = connection.execute(
                text(query)
            ).scalar_one()

            print(f"{table:20s}: {count:>8,}")

        print("\nIMPORT HISTORY")
        print("=" * 50)

        results = connection.execute(
            text("""
                SELECT
                    id,
                    file_name,
                    import_type,
                    total_rows,
                    accepted_rows,
                    rejected_rows,
                    status
                FROM import_logs
                ORDER BY id
            """)
        ).mappings().all()

        for row in results:
            print(
                f"ID: {row['id']} | "
                f"Type: {row['import_type']} | "
                f"Total: {row['total_rows']} | "
                f"Accepted: {row['accepted_rows']} | "
                f"Rejected: {row['rejected_rows']} | "
                f"Status: {row['status']}"
            )

        print("\nVERIFICATION COMPLETED")


if __name__ == "__main__":
    main()
