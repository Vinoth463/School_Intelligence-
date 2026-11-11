
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


class Examination(Base):
    __tablename__ = "examinations"

    __table_args__ = (
        UniqueConstraint(
            "institution_id",
            "academic_period_id",
            "name",
            name="uq_exam_institution_period_name",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_exam_name_not_empty",
        ),
        CheckConstraint(
            "exam_date >= start_date",
            name="ck_exam_date_after_start",
        ),
        CheckConstraint(
            "exam_date <= end_date",
            name="ck_exam_date_before_end",
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="ck_exam_valid_date_range",
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

    academic_period_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("academic_periods.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    exam_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
