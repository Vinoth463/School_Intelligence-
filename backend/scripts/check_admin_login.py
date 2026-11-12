
from getpass import getpass

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.core.security import verify_password
from app.models import User


def main():
    email = "vinothsree4@gmail.com"
    password = getpass("Enter your admin password: ")

    db = SessionLocal()

    try:
        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        print("\nADMIN LOGIN DIAGNOSTICS")
        print("-----------------------")

        print("User found:", user is not None)

        if user is None:
            return

        print("User ID:", user.id)
        print("Institution ID:", user.institution_id)
        print("Account active:", user.is_active)
        print("Password matches:", verify_password(
            password,
            user.hashed_password
        ))

    finally:
        db.close()


if __name__ == "__main__":
    main()
