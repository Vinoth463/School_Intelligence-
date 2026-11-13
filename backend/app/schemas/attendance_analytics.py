
from datetime import date

from pydantic import BaseModel


class StudentAttendanceResponse(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str

    class_id: int
    grade: str
    section: str

    total_sessions: int
    present_sessions: int
    absent_sessions: int
    attendance_percentage: float | None


class SubjectAttendanceResponse(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str

    total_sessions: int
    present_sessions: int
    absent_sessions: int
    students_recorded: int
    attendance_percentage: float | None


class ClassAttendanceResponse(BaseModel):
    class_id: int
    grade: str
    section: str
    academic_period_id: int

    total_sessions: int
    present_sessions: int
    absent_sessions: int
    students_recorded: int
    attendance_percentage: float | None


class LowAttendanceResponse(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str

    class_id: int
    grade: str
    section: str

    total_sessions: int
    present_sessions: int
    absent_sessions: int
    attendance_percentage: float

class StudentSubjectAttendanceResponse(BaseModel):
    student_id: int
    admission_number: str
    first_name: str
    last_name: str

    class_id: int
    grade: str
    section: str

    subject_id: int
    subject_name: str
    subject_code: str

    total_sessions: int
    present_sessions: int
    absent_sessions: int
    attendance_percentage: float | None

class AcademicPeriodAttendanceComparisonResponse(BaseModel):
    academic_period_id: int
    academic_period_name: str
    start_date: date
    end_date: date

    total_sessions: int
    present_sessions: int
    absent_sessions: int
    students_recorded: int

    attendance_percentage: float | None


    