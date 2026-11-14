
import api from "./api";

import type {
  ImportHistoryParams,
  ImportHistoryResponse,
  ImportRejectionParams,
  ImportRejectionResponse,
  ImportSummary,
  ImportType,
} from "../types/imports";

/**
 * Upload an academic data file.
 * Supports students, marks and attendance.
 */
export const uploadImportFile = async (
  importType: ImportType,
  file: File
): Promise<ImportSummary> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<ImportSummary>(
    `/imports/${importType}`,
    formData
  );

  return response.data;
};

/**
 * Fetch import history with pagination and optional type filter.
 */
export const getImportHistory = async (
  params: ImportHistoryParams = {}
): Promise<ImportHistoryResponse> => {
  const response = await api.get<ImportHistoryResponse>(
    "/imports/history",
    {
      params,
    }
  );

  return response.data;
};

/**
 * Fetch rejected rows for a specific import.
 */
export const getImportRejections = async (
  importId: number,
  params: ImportRejectionParams = {}
): Promise<ImportRejectionResponse> => {
  const response = await api.get<ImportRejectionResponse>(
    `/imports/${importId}/rejections`,
    {
      params,
    }
  );

  return response.data;
};
