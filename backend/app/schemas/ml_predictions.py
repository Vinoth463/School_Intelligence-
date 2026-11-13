
from typing import Literal

from pydantic import BaseModel, Field


class UnderperformancePredictionRequest(BaseModel):
    student_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)
    target_examination_id: int = Field(gt=0)


class PredictionFeaturesResponse(BaseModel):
    previous_exam_percentage: float
    historical_average_percentage: float
    marks_trend: float | None
    previous_exam_count: int

    attendance_percentage: float | None
    attendance_recent_60d: float | None
    attendance_previous_60d: float | None
    attendance_trend: float | None
    attendance_sessions_to_date: int

    class_grade: str


class UnderperformancePredictionResponse(BaseModel):
    student_id: int
    subject_id: int
    target_examination_id: int

    predicted_underperformance: bool
    underperformance_score: float

    score_interpretation: str
    classification_threshold: float
    academic_marks_threshold: float

    risk_category: Literal["low", "medium", "high"]
    risk_indicators: list[str]
    positive_indicators: list[str]

    data_sufficiency_status: Literal["limited", "more_complete"]
    data_sufficiency_warnings: list[str]
    historical_examination_count: int
    historical_attendance_sessions: int

    model_name: str
    prediction_type: str
    data_type: str

    features: PredictionFeaturesResponse
