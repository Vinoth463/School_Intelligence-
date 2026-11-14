
export type ImportType = "students" | "marks" | "attendance";

export type ImportStatus = "processing" | "completed" | "failed";

export interface ImportSummary {
  import_id: number;
  file_name: string;
  import_type: ImportType;
  total_rows: number;
  accepted_rows: number;
  rejected_rows: number;
  status: ImportStatus;
}

export interface ImportHistoryItem {
  id: number;
  file_name: string;
  import_type: ImportType;
  status: ImportStatus;
  total_rows: number;
  accepted_rows: number;
  rejected_rows: number;
  uploaded_by: number;
  created_at: string;
  completed_at: string | null;
}

export interface ImportHistoryResponse {
  total: number;
  items: ImportHistoryItem[];
}

export interface ImportRejection {
  id: number;
  import_log_id: number;
  row_number: number;
  rejection_reason: string;
  raw_data: Record<string, unknown>;
  created_at: string;
}

export interface ImportRejectionResponse {
  import_id: number;
  total: number;
  items: ImportRejection[];
}

export interface ImportHistoryParams {
  limit?: number;
  offset?: number;
  import_type?: ImportType;
}

export interface ImportRejectionParams {
  limit?: number;
  offset?: number;
}
