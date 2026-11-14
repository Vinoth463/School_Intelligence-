
import api from "./api";

import type {
  ReportType,
  ReportFilters,
  ReportFilterOptions,
} from "../types/reports";

export interface ReportRequest extends ReportFilters {
  report_type: ReportType;
}

// Fetch overview report
export const getOverviewReport = async (
  filters?: ReportFilters
) => {
  const response = await api.get("/reports/overview", {
    params: filters,
  });

  return response.data;
};

// Fetch individual student report
export const getStudentReport = async (
  studentId: number,
  filters?: ReportFilters
) => {
  const response = await api.get(
    `/reports/students/${studentId}`,
    { params: filters }
  );

  return response.data;
};

// Fetch subject performance report
export const getSubjectsReport = async (
  filters?: ReportFilters
) => {
  const response = await api.get("/reports/subjects", {
    params: filters,
  });

  return response.data;
};

// Fetch class performance report
export const getClassesReport = async (
  filters?: ReportFilters
) => {
  const response = await api.get("/reports/classes", {
    params: filters,
  });

  return response.data;
};

// Fetch attendance report
export const getAttendanceReport = async (
  filters?: ReportFilters
) => {
  const response = await api.get("/reports/attendance", {
    params: filters,
  });

  return response.data;
};

// Download Excel report
export const downloadExcelReport = async (
  request: ReportRequest
): Promise<Blob> => {
  const response = await api.get("/reports/export/excel", {
    params: request,
    responseType: "blob",
  });

  return response.data;
};

// Download PDF report
export const downloadPdfReport = async (
  request: ReportRequest
): Promise<Blob> => {
  const response = await api.get("/reports/export/pdf", {
    params: request,
    responseType: "blob",
  });

  return response.data;
};

// Fetch dynamic report filter options
export const getReportFilterOptions = async (
  academicPeriodId?: number,
  classId?: number
): Promise<ReportFilterOptions> => {
  const response = await api.get("/reports/filter-options", {
    params: {
      academic_period_id: academicPeriodId,
      class_id: classId,
    },
  });

  return response.data;
};
