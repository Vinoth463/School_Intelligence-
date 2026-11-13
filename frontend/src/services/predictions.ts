
import api from "./api";

import type {
  StudentOption,
  SubjectOption,
  ExaminationOption,
  PredictionRequest,
  UnderperformancePrediction,
} from "../types/predictions";

const predictionsService = {
  // Fetch active students belonging to the institution.
  async getStudents(): Promise<StudentOption[]> {
    const response = await api.get<StudentOption[]>(
      "/ml/options/students"
    );

    return response.data;
  },

  // Fetch available subjects.
  async getSubjects(): Promise<SubjectOption[]> {
    const response = await api.get<SubjectOption[]>(
      "/ml/options/subjects"
    );

    return response.data;
  },

  // Fetch eligible future examinations for the selected student and subject.
  async getExaminations(
    studentId: number,
    subjectId: number
  ): Promise<ExaminationOption[]> {
    const response = await api.get<ExaminationOption[]>(
      "/ml/options/examinations",
      {
        params: {
          student_id: studentId,
          subject_id: subjectId,
        },
      }
    );

    return response.data;
  },

  // Generate an underperformance prediction.
  async predict(
    payload: PredictionRequest
  ): Promise<UnderperformancePrediction> {
    const response = await api.post<UnderperformancePrediction>(
      "/ml/predictions/underperformance",
      payload
    );

    return response.data;
  },
};

export default predictionsService;
