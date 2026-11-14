
export type ReportType =
  | "overview"
  | "student"
  | "subjects"
  | "classes"
  | "attendance";

export interface ReportFilters {
  academic_period_id?: number;
  student_id?: number;
  examination_id?: number;
  class_id?: number;
  threshold?: number;
}

export interface ReportMetric {
  label: string;
  value: string | number;
}

export interface SubjectPerformance {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  total_mark_records: number;
  students_evaluated: number;
  average_percentage: number;
  highest_percentage: number;
  lowest_percentage: number;
  grade_a_count?: number;
  grade_b_count?: number;
  grade_c_count?: number;
}

export interface ClassPerformance {
  class_id: number;
  grade: string;
  section: string;
  academic_period_id: number;
  total_mark_records: number;
  students_evaluated: number;
  average_percentage: number;
  highest_percentage: number;
  lowest_percentage: number;
  subjects?: SubjectPerformance[];
}

export interface ClassAttendance {
  class_id: number;
  grade: string;
  section: string;
  academic_period_id: number;
  total_sessions: number;
  present_sessions: number;
  absent_sessions: number;
  students_recorded: number;
  attendance_percentage: number;
}

export interface StudentReport {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  examinations: Array<Record<string, unknown>>;
  performance_trend: Array<Record<string, unknown>>;
  attendance?: Array<Record<string, unknown>>;
}

export interface OverviewReport {
  institution_id: number;
  academic_period_id?: number | null;
  total_students: number;
  average_performance_percentage: number;
  total_mark_records: number;
  total_attendance_sessions: number;
  present_attendance_sessions: number;
  attendance_percentage: number;
  subject_performance?: SubjectPerformance[];
  class_performance?: ClassPerformance[];
  class_attendance?: ClassAttendance[];
}

export interface AttendanceReport {
  class_attendance: ClassAttendance[];
  student_attendance?: Array<Record<string, unknown>>;
  low_attendance_students?: Array<Record<string, unknown>>;
}


export interface ReportAcademicPeriodOption {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

export interface ReportClassOption {
  id: number;
  grade: string;
  section: string;
  academic_period_id: number;
  label: string;
}

export interface ReportExaminationOption {
  id: number;
  name: string;
  academic_period_id: number;
  exam_date: string;
}

export interface ReportStudentOption {
  id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  class_id: number;
  label: string;
}

export interface ReportFilterOptions {
  academic_periods: ReportAcademicPeriodOption[];
  classes: ReportClassOption[];
  examinations: ReportExaminationOption[];
  students: ReportStudentOption[];
}
