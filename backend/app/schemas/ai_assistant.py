
from pydantic import BaseModel, Field


class AcademicAssistantRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Academic question asked by the user",
    )

    # Academic filtering
    academic_period_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional academic period filter",
    )

    class_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional classroom filter",
    )

    subject_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional subject filter",
    )

    student_id: int | None = Field(
        default=None,
        gt=0,
        description="Optional student filter",
    )

    # Required for future examination ML explanations
    target_examination_id: int | None = Field(
        default=None,
        gt=0,
        description="Future examination ID for ML underperformance analysis",
    )


class AcademicAssistantResponse(BaseModel):
    answer: str

    data_used: list[str] = Field(
        default_factory=list,
        description="Academic data sources used to generate the answer",
    )

    records_found: int = Field(
        default=0,
        ge=0,
        description="Number of academic records retrieved",
    )
