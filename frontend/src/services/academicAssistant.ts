import api from "./api";
import type {
  AcademicAssistantRequest,
  AcademicAssistantResponse,
} from "../types/academicAssistant";

export const askAcademicAssistant = async (
  payload: AcademicAssistantRequest
): Promise<AcademicAssistantResponse> => {
  const response = await api.post<AcademicAssistantResponse>(
    "/ai/academic-assistant",
    payload
  );

  return response.data;
};