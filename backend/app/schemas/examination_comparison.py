
from datetime import date

from pydantic import BaseModel


class ExaminationSubjectComparison(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str

    total_mark_records: int
    students_evaluated: int

    average_percentage: float
    highest_percentage: float
    lowest_percentage: float

    change_from_previous: float | None = None


class ExaminationComparisonItem(BaseModel):
    examination_id: int
    examination_name: str
    exam_date: date

    total_mark_records: int
    students_evaluated: int

    average_percentage: float
    highest_percentage: float
    lowest_percentage: float

    change_from_previous: float | None = None

    subjects: list[ExaminationSubjectComparison]


class ExaminationComparisonResponse(BaseModel):
    academic_period_id: int
    class_id: int | None = None
    subject_id: int | None = None

    examinations: list[ExaminationComparisonItem]
