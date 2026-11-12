
from datetime import date
from pydantic import BaseModel


class StudentSubjectPerformance(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str
    obtained_marks: float
    max_marks: float
    percentage: float


class StudentExaminationPerformance(BaseModel):
    examination_id: int
    examination_name: str
    academic_period_id: int
    exam_date: date

    total_obtained_marks: float
    total_max_marks: float
    overall_percentage: float

    subjects: list[StudentSubjectPerformance]


class StudentPerformanceTrend(BaseModel):
    examination_id: int
    examination_name: str
    overall_percentage: float
    change_from_previous: float | None


class StudentPerformanceResponse(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str

    examinations: list[StudentExaminationPerformance]
    performance_trend: list[StudentPerformanceTrend]
