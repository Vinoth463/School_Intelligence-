
from pydantic import BaseModel


class DecliningPerformanceResponse(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str

    academic_period_id: int
    class_id: int

    previous_examination_id: int
    previous_examination_name: str

    examination_id: int
    examination_name: str

    previous_percentage: float
    current_percentage: float
    percentage_change: float

    performance_status: str


class SubjectDeclineResponse(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str

    subject_id: int
    subject_name: str
    subject_code: str

    previous_examination_name: str
    examination_name: str

    previous_percentage: float
    current_percentage: float
    percentage_change: float
