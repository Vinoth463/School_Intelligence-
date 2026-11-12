
from pydantic import BaseModel, ConfigDict


class DashboardOverviewResponse(BaseModel):
    institution_id: int
    academic_period_id: int | None

    total_students: int

    average_performance_percentage: float
    total_mark_records: int

    total_attendance_sessions: int
    present_attendance_sessions: int
    attendance_percentage: float

    model_config = ConfigDict(from_attributes=True)
