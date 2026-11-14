
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ImportType = Literal["students", "marks", "attendance"]

ImportStatus = Literal["processing", "completed", "failed"]


class ImportSummaryResponse(BaseModel):
    import_id: int
    file_name: str
    import_type: ImportType
    total_rows: int = Field(ge=0)
    accepted_rows: int = Field(ge=0)
    rejected_rows: int = Field(ge=0)
    status: ImportStatus

    model_config = ConfigDict(from_attributes=True)


class ImportHistoryItem(BaseModel):
    id: int
    file_name: str
    import_type: ImportType
    status: ImportStatus
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    uploaded_by: int
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ImportHistoryResponse(BaseModel):
    total: int = Field(ge=0)
    items: list[ImportHistoryItem]


class ImportRejectionResponse(BaseModel):
    id: int
    import_log_id: int
    row_number: int
    rejection_reason: str
    raw_data: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImportRejectionListResponse(BaseModel):
    import_id: int
    total: int = Field(ge=0)
    items: list[ImportRejectionResponse]
