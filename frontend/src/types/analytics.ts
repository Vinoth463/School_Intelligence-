
export interface SubjectAnalytics {
  subject_id: number;
  subject_name: string;
  subject_code: string;

  total_mark_records: number;
  students_evaluated: number;

  average_percentage: number;
  highest_percentage: number;
  lowest_percentage: number;

  grade_a_count: number;
  grade_b_count: number;
  grade_c_count: number;
  grade_d_count: number;
  grade_e_count: number;
  grade_f_count: number;
}

export interface SubjectAnalyticsFilters {
  academic_period_id?: number;
  examination_id?: number;
  class_id?: number;
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
}

export interface ExaminationOption {
  examination_id: number;
  examination_name: string;
  exam_date: string;
}

export interface PeriodOption {
  academic_period_id: number;
  academic_period_name: string;
}

export interface ExaminationComparison {
  academic_period_id: number;
  class_id: number | null;
  subject_id: number | null;
  examinations: ExaminationOption[];
}

export interface PeriodComparison {
  class_id: number | null;
  subject_id: number | null;
  periods: PeriodOption[];
}
