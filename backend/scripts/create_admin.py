
from getpass import getpass

from argon2 import PasswordHasher
from argon2.exceptions import HashingError
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models import Institution, User


password_hasher = PasswordHasher()


def create_admin():
    print("\n=== School Intelligence: Initial Admin Setup ===\n")

    full_name = input("Administrator full name: ").strip()
    email = input("Administrator email: ").strip().lower()

    if not full_name or len(full_name) > 150:
        raise ValueError("Enter a valid name (maximum 150 characters).")

    if not email or len(email) > 255 or "@" not in email:
        raise ValueError("Enter a valid email address.")

    institution_input = input(
        "Institution ID [1]: "
    ).strip()

    institution_id = int(institution_input or "1")

    password = getpass("Create password (minimum 12 characters): ")
    confirmation = getpass("Confirm password: ")

    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")

    if password != confirmation:
        raise ValueError("Passwords do not match.")

    # Hash the password before storing it.
    hashed_password = password_hasher.hash(password)

    with SessionLocal.begin() as db:
        institution = db.scalar(
            select(Institution).where(
                Institution.id == institution_id
            )
        )

        if institution is None:
            raise ValueError("Institution does not exist.")

        existing_user = db.scalar(
            select(User.id).where(
                User.institution_id == institution_id,
                User.email == email,
            )
        )

        if existing_user is not None:
            raise ValueError(
                "An account with this email already exists "
                "for this institution."
            )

        admin = User(
            institution_id=institution_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.flush()

        admin_id = admin.id

    print("\nAdministrator created successfully.")
    print(f"Admin ID: {admin_id}")
    print(f"Institution ID: {institution_id}")
    print(f"Email: {email}")
    print("Role: admin")
    print("Password storage: Argon2 hash")


if __name__ == "__main__":
    try:
        create_admin()
    except (ValueError, HashingError) as exc:
        print(f"\nADMIN CREATION FAILED: {exc}")
        raise SystemExit(1)
    except Exception as exc:
        print(f"\nADMIN CREATION FAILED: {exc}")
        raise SystemExit(1)
