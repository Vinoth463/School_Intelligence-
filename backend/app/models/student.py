
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Student(Base):
    __tablename__ = "students"

    __table_args__ = (
        UniqueConstraint(
            "institution_id",
            "admission_number",
            name="uq_student_institution_admission",
        ),
        CheckConstraint(
            "length(trim(first_name)) > 0",
            name="ck_student_first_name_not_empty",
        ),
        CheckConstraint(
            "length(trim(last_name)) > 0",
            name="ck_student_last_name_not_empty",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'transferred', 'graduated')",
            name="ck_student_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    institution_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    admission_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    admission_date: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date(),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        server_default="active",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
