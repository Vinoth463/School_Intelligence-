
from pydantic import BaseModel


class SubjectPerformanceResponse(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str

    total_mark_records: int
    students_evaluated: int

    average_percentage: float
    highest_percentage: float
    lowest_percentage: float

    grade_a_count: int
    grade_b_count: int
    grade_c_count: int
    grade_d_count: int
    grade_e_count: int
    grade_f_count: int
