
export interface StudentOption {
  id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  name: string;
  class_id: number;
}

export interface SubjectOption {
  id: number;
  name: string;
  code: string;
}

export interface ExaminationOption {
  id: number;
  name: string;
  exam_date: string;
  academic_period_id: number;
}

export interface PredictionRequest {
  student_id: number;
  subject_id: number;
  target_examination_id: number;
}

export interface PredictionFeatures {
  previous_exam_percentage: number | null;
  historical_average_percentage: number | null;
  marks_trend: number | null;
  previous_exam_count: number;
  attendance_percentage: number | null;
  attendance_recent_60d: number | null;
  attendance_previous_60d: number | null;
  attendance_trend: number | null;
  attendance_sessions_to_date: number;
  class_grade: string;
}

export interface UnderperformancePrediction {
  student_id: number;
  subject_id: number;
  target_examination_id: number;

  predicted_underperformance: boolean;
  underperformance_score: number;
  score_interpretation: string;

  classification_threshold: number;
  academic_marks_threshold: number;
  risk_category: string;

  risk_indicators: string[];
  positive_indicators: string[];

  data_sufficiency_status: string;
  data_sufficiency_warnings: string[];

  historical_examination_count: number;
  historical_attendance_sessions: number;

  model_name: string;
  prediction_type: string;
  data_type: string;

  features: PredictionFeatures;
}
