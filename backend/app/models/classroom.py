
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Classroom(Base):
    __tablename__ = "classes"

    __table_args__ = (
        UniqueConstraint(
            "institution_id",
            "academic_period_id",
            "grade",
            "section",
            name="uq_class_institution_period_grade_section",
        ),
        CheckConstraint(
            "length(trim(grade)) > 0",
            name="ck_class_grade_not_empty",
        ),
        CheckConstraint(
            "length(trim(section)) > 0",
            name="ck_class_section_not_empty",
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

    grade: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    section: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
