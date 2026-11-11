
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Mark(Base):
    __tablename__ = "marks"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "examination_id",
            "subject_id",
            name="uq_mark_student_exam_subject",
        ),
        CheckConstraint(
            "obtained_marks >= 0",
            name="ck_mark_obtained_non_negative",
        ),
        CheckConstraint(
            "max_marks > 0",
            name="ck_mark_max_positive",
        ),
        CheckConstraint(
            "obtained_marks <= max_marks",
            name="ck_mark_not_above_max",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    examination_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("examinations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    obtained_marks: Mapped[Decimal] = mapped_column(
        Numeric(7, 2),
        nullable=False,
    )

    max_marks: Mapped[Decimal] = mapped_column(
        Numeric(7, 2),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
