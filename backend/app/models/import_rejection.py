
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ImportRejection(Base):
    __tablename__ = "import_rejections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    import_log_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("import_logs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    row_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    rejection_reason: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    raw_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
