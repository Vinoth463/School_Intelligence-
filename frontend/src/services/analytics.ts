
import api from "./api";

import type {
  SubjectAnalytics,
  SubjectAnalyticsFilters,
  ClassPerformance,
  ExaminationComparison,
  PeriodComparison,
} from "../types/analytics";

export const analyticsService = {
  // Subject analytics
  async getSubjectAnalytics(
    filters: SubjectAnalyticsFilters = {}
  ): Promise<SubjectAnalytics[]> {
    const response = await api.get<SubjectAnalytics[]>(
      "/analytics/subjects",
      {
        params: filters,
      }
    );

    return response.data;
  },

  // Class performance
  async getClassPerformance(
    academicPeriodId?: number,
    examinationId?: number
  ): Promise<ClassPerformance[]> {
    const response = await api.get<ClassPerformance[]>(
      "/analytics/classes/performance",
      {
        params: {
          academic_period_id: academicPeriodId,
          examination_id: examinationId,
        },
      }
    );

    return response.data;
  },

  // Examination comparison
  async getExaminationComparison(
    academicPeriodId: number,
    classId?: number
  ): Promise<ExaminationComparison> {
    const response = await api.get<ExaminationComparison>(
      "/analytics/examinations/comparison",
      {
        params: {
          academic_period_id: academicPeriodId,
          class_id: classId,
        },
      }
    );

    return response.data;
  },

  // Academic period comparison
  async getPeriodComparison(
    classId?: number
  ): Promise<PeriodComparison> {
    const response = await api.get<PeriodComparison>(
      "/analytics/periods/comparison",
      {
        params: {
          class_id: classId,
        },
      }
    );

    return response.data;
  },
};

export default analyticsService;
