
from pydantic import BaseModel, Field


class AttendancePerformanceStudent(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str
    academic_period_id: int
    class_id: int
    total_sessions: int
    present_sessions: int
    attendance_percentage: float
    total_obtained: float
    total_maximum: float
    performance_percentage: float
    analysis_category: str


class AttendancePerformanceAnalysisResponse(BaseModel):
    institution_id: int
    academic_period_id: int | None
    class_id: int | None

    total_students_analyzed: int
    attendance_performance_correlation: float | None
    correlation_interpretation: str

    high_attendance_threshold: float
    low_attendance_threshold: float
    low_marks_threshold: float
    high_marks_threshold: float

    high_attendance_low_performance_count: int
    low_attendance_high_performance_count: int

    high_attendance_low_performance: list[AttendancePerformanceStudent]
    low_attendance_high_performance: list[AttendancePerformanceStudent]
    student_records: list[AttendancePerformanceStudent]
