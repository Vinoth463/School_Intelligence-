
from pydantic import BaseModel


class PeriodSubjectComparison(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str
    total_mark_records: int
    students_evaluated: int
    average_percentage: float
    highest_percentage: float
    lowest_percentage: float
    change_from_previous_period: float | None = None


class PeriodComparisonItem(BaseModel):
    academic_period_id: int
    academic_period_name: str
    total_examinations: int
    total_mark_records: int
    students_evaluated: int
    average_percentage: float
    highest_percentage: float
    lowest_percentage: float
    change_from_previous_period: float | None = None
    subjects: list[PeriodSubjectComparison]


class PeriodComparisonResponse(BaseModel):
    class_id: int | None = None
    subject_id: int | None = None
    periods: list[PeriodComparisonItem]
