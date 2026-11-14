
export interface AcademicAssistantRequest {
  question: string;
  academic_period_id?: number;
  class_id?: number;
  subject_id?: number;
  student_id?: number;
  target_examination_id?: number;
}

export interface AcademicAssistantResponse {
  answer: string;
  data_used: string[];
  records_found: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  data_used?: string[];
  records_found?: number;
  timestamp: Date;
}
