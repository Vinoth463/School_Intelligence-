
from pydantic import BaseModel


class ClassSubjectPerformance(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str

    total_mark_records: int
    students_evaluated: int

    average_percentage: float
    highest_percentage: float
    lowest_percentage: float


class ClassPerformanceResponse(BaseModel):
    class_id: int
    grade: str
    section: str
    academic_period_id: int

    total_mark_records: int
    students_evaluated: int

    average_percentage: float
    highest_percentage: float
    lowest_percentage: float

    subjects: list[ClassSubjectPerformance]
