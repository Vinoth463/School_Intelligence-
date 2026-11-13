
export interface DashboardOverview {
  institution_id: number;
  academic_period_id: number | null;
  total_students: number;
  average_performance_percentage: number;
  total_mark_records: number;
  total_attendance_sessions: number;
  present_attendance_sessions: number;
  attendance_percentage: number;
}
