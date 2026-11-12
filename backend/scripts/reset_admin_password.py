
from getpass import getpass

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.core.security import hash_password, verify_password
from app.models import User


def main():
    email = "vinothsree4@gmail.com"

    password = getpass("Enter new admin password: ")
    confirm_password = getpass("Confirm new admin password: ")

    if len(password) < 12:
        print("Password must contain at least 12 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    db = SessionLocal()

    try:
        with db.begin():
            user = db.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()

            if user is None:
                print("Admin account not found.")
                return

            user.hashed_password = hash_password(password)

        print("\nAdmin password updated successfully.")

        # Verify the newly stored Argon2 hash.
        db.expire_all()

        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one()

        print(
            "Password verification:",
            verify_password(password, user.hashed_password)
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
