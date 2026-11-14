
export interface StudentAttendance {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  class_id: number;
  grade: string;
  section: string;
  total_sessions: number;
  present_sessions: number;
  absent_sessions: number;
  attendance_percentage: number | null;
}

export interface SubjectAttendance {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  total_sessions: number;
  present_sessions: number;
  absent_sessions: number;
  students_recorded: number;
  attendance_percentage: number | null;
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
  attendance_percentage: number | null;
}

export interface LowAttendanceStudent {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  class_id: number;
  grade: string;
  section: string;
  total_sessions: number;
  present_sessions: number;
  absent_sessions: number;
  attendance_percentage: number;
}

export interface StudentSubjectAttendance {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  class_id: number;
  grade: string;
  section: string;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  total_sessions: number;
  present_sessions: number;
  absent_sessions: number;
  attendance_percentage: number | null;
}

export interface AcademicPeriodAttendanceComparison {
  academic_period_id: number;
  academic_period_name: string;
  start_date: string;
  end_date: string;
  total_sessions: number;
  present_sessions: number;
  absent_sessions: number;
  students_recorded: number;
  attendance_percentage: number | null;
}
