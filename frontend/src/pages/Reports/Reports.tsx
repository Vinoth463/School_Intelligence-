
import { useEffect, useState } from "react";

import {
  getOverviewReport,
  getStudentReport,
  getSubjectsReport,
  getClassesReport,
  getAttendanceReport,
  getReportFilterOptions,
  downloadExcelReport,
  downloadPdfReport,
} from "../../services/reports";

import type {
  ReportType,
  ReportFilters,
  ReportFilterOptions,
} from "../../types/reports";

import "./Reports.css";

const reportOptions: {
  value: ReportType;
  label: string;
  description: string;
}[] = [
  {
    value: "overview",
    label: "Overview Report",
    description: "Institution-wide academic summary.",
  },
  {
    value: "student",
    label: "Student Report",
    description: "Individual student performance and attendance.",
  },
  {
    value: "subjects",
    label: "Subject Report",
    description: "Compare all subjects across the institution or a selected class.",
  },
  {
    value: "classes",
    label: "Class Report",
    description: "Compare classes with subject-wise performance details.",
  },
  {
    value: "attendance",
    label: "Attendance Report",
    description: "Class and student attendance summaries.",
  },
];

const emptyOptions: ReportFilterOptions = {
  academic_periods: [],
  classes: [],
  examinations: [],
  students: [],
};

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "-";

  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }

  if (typeof value === "boolean") return value ? "Yes" : "No";

  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}T/.test(value)) {
    return new Date(value).toLocaleDateString();
  }

  return String(value);
}

function formatLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function getRecords(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) return [];

  return value.filter(
    (item): item is Record<string, unknown> =>
      typeof item === "object" &&
      item !== null &&
      !Array.isArray(item)
  );
}

function MetricCards({
  items,
}: {
  items: { label: string; value: string | number }[];
}) {
  return (
    <div className="reports-metric-grid">
      {items.map((item) => (
        <div className="reports-metric-card" key={item.label}>
          <span>{item.label}</span>
          <strong>{item.value}</strong>
        </div>
      ))}
    </div>
  );
}

function DataTable({
  data,
  columns,
}: {
  data: unknown[];
  columns?: string[];
}) {
  const rows = getRecords(data);

  if (rows.length === 0) {
    return <p className="reports-empty">No records available.</p>;
  }

  const keys =
    columns ??
    Array.from(new Set(rows.flatMap((row) => Object.keys(row)))).filter(
      (key) =>
        rows.some(
          (row) =>
            row[key] === null ||
            typeof row[key] !== "object"
        )
    );

  if (keys.length === 0) {
    return <p className="reports-empty">No tabular data available.</p>;
  }

  return (
    <div className="reports-table-wrapper">
      <table className="reports-table">
        <thead>
          <tr>
            {keys.map((key) => (
              <th key={key}>{formatLabel(key)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {keys.map((key) => (
                <td key={key}>{formatValue(row[key])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StudentReportView({
  data,
}: {
  data: Record<string, unknown>;
}) {
  const studentValue = data.student;
  const student =
    typeof studentValue === "object" && studentValue !== null
      ? (studentValue as Record<string, unknown>)
      : data;

  const examinations = getRecords(student.examinations);
  const attendance = getRecords(data.attendance ?? student.attendance);
  const trend = getRecords(student.performance_trend);

  const studentName = [student.first_name, student.last_name]
    .filter(Boolean)
    .join(" ");

  const average =
    examinations.length > 0
      ? examinations.reduce(
          (sum, exam) => sum + Number(exam.overall_percentage ?? 0),
          0
        ) / examinations.length
      : 0;

  const totalAttendance = attendance.reduce(
    (sum, row) => sum + Number(row.total_sessions ?? 0),
    0
  );
  const presentAttendance = attendance.reduce(
    (sum, row) => sum + Number(row.present_sessions ?? 0),
    0
  );
  const absentAttendance = attendance.reduce(
    (sum, row) => sum + Number(row.absent_sessions ?? 0),
    0
  );

  const attendancePercentage =
    totalAttendance > 0
      ? (presentAttendance / totalAttendance) * 100
      : null;

  const subjectRows = examinations.flatMap((exam) =>
    getRecords(exam.subjects).map((subject) => ({
      examination_name: exam.examination_name,
      subject_name: subject.subject_name,
      subject_code: subject.subject_code,
      obtained_marks: subject.obtained_marks,
      max_marks: subject.max_marks,
      percentage: subject.percentage,
    }))
  );

  return (
    <div className="reports-results">
      <section className="reports-result-section">
        <h3>Student Information</h3>
        <MetricCards
          items={[
            { label: "Student Name", value: studentName || "-" },
            {
              label: "Admission Number",
              value: formatValue(student.admission_number),
            },
            { label: "Student ID", value: formatValue(student.student_id) },
            { label: "Examinations", value: examinations.length },
          ]}
        />
      </section>

      <section className="reports-result-section">
        <h3>Academic Performance Summary</h3>
        <MetricCards
          items={[
            {
              label: "Average Examination Percentage",
              value: `${average.toFixed(2)}%`,
            },
            { label: "Examinations Completed", value: examinations.length },
            { label: "Total Attendance Sessions", value: totalAttendance },
            {
              label: "Attendance Percentage",
              value:
                attendancePercentage === null
                  ? "-"
                  : `${attendancePercentage.toFixed(2)}%`,
            },
          ]}
        />
      </section>

      <section className="reports-result-section">
        <h3>Examination Results</h3>
        <DataTable
          data={examinations}
          columns={[
            "examination_name",
            "exam_date",
            "total_obtained_marks",
            "total_max_marks",
            "overall_percentage",
          ]}
        />
      </section>

      <section className="reports-result-section">
        <h3>Subject-wise Performance</h3>
        <DataTable
          data={subjectRows}
          columns={[
            "examination_name",
            "subject_name",
            "subject_code",
            "obtained_marks",
            "max_marks",
            "percentage",
          ]}
        />
      </section>

      <section className="reports-result-section">
        <h3>Performance Trend</h3>
        <DataTable
          data={trend}
          columns={[
            "examination_name",
            "overall_percentage",
            "change_from_previous",
          ]}
        />
      </section>

      <section className="reports-result-section">
        <h3>Attendance Summary</h3>
        <MetricCards
          items={[
            { label: "Total Sessions", value: totalAttendance },
            { label: "Present Sessions", value: presentAttendance },
            { label: "Absent Sessions", value: absentAttendance },
            {
              label: "Attendance",
              value:
                attendancePercentage === null
                  ? "-"
                  : `${attendancePercentage.toFixed(2)}%`,
            },
          ]}
        />
        <DataTable data={attendance} />
      </section>
    </div>
  );
}

function GenericReportView({
  data,
}: {
  data: Record<string, unknown>;
}) {
  return (
    <div className="reports-results">
      {Object.entries(data).map(([key, value]) => {
        if (value === null || value === undefined) return null;

        if (Array.isArray(value)) {
          return (
            <section className="reports-result-section" key={key}>
              <h3>{formatLabel(key)}</h3>
              <DataTable data={value} />
            </section>
          );
        }

        if (typeof value === "object") {
          return (
            <section className="reports-result-section" key={key}>
              <h3>{formatLabel(key)}</h3>
              <GenericReportView
                data={value as Record<string, unknown>}
              />
            </section>
          );
        }

        return (
          <section className="reports-result-section" key={key}>
            <h3>{formatLabel(key)}</h3>
            <p className="reports-metric-value">{formatValue(value)}</p>
          </section>
        );
      })}
    </div>
  );
}

function ReportResults({ data }: { data: unknown }) {
  if (!data || typeof data !== "object") {
    return <p className="reports-empty">No report data available.</p>;
  }

  if (Array.isArray(data)) {
    return <DataTable data={data} />;
  }

  const report = data as Record<string, unknown>;

  if (report.student && typeof report.student === "object") {
    return <StudentReportView data={report} />;
  }

  return <GenericReportView data={report} />;
}

function Reports() {
  const [reportType, setReportType] =
    useState<ReportType>("overview");

  const [options, setOptions] =
    useState<ReportFilterOptions>(emptyOptions);

  const [academicPeriodId, setAcademicPeriodId] =
    useState("");

  const [classId, setClassId] = useState("");
  const [examinationId, setExaminationId] = useState("");
  const [studentId, setStudentId] = useState("");
  const [threshold, setThreshold] = useState("75");

  const [reportData, setReportData] =
    useState<unknown>(null);

  const [loadingOptions, setLoadingOptions] =
    useState(true);

  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const [error, setError] = useState("");
  const [reportGenerated, setReportGenerated] =
    useState(false);

  // Load dropdown options and refresh dependent lists.
  useEffect(() => {
    let cancelled = false;

    const loadOptions = async () => {
      setLoadingOptions(true);
      setError("");

      try {
        const response = await getReportFilterOptions(
          academicPeriodId
            ? Number(academicPeriodId)
            : undefined,
          classId ? Number(classId) : undefined
        );

        if (!cancelled) {
          setOptions(response);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          const message =
            err instanceof Error
              ? err.message
              : "Unable to load report filters.";

          setError(message);
        }
      } finally {
        if (!cancelled) {
          setLoadingOptions(false);
        }
      }
    };

    loadOptions();

    return () => {
      cancelled = true;
    };
  }, [academicPeriodId, classId]);

  const selectedReport = reportOptions.find(
    (report) => report.value === reportType
  );

  const selectedPeriod = options.academic_periods.find(
    (period) => period.id === Number(academicPeriodId)
  );

  const buildFilters = (): ReportFilters => {
    const result: ReportFilters = {};

    if (academicPeriodId) {
      result.academic_period_id = Number(academicPeriodId);
    }

    if (classId) {
      result.class_id = Number(classId);
    }

    if (examinationId) {
      result.examination_id = Number(examinationId);
    }

    if (studentId) {
      result.student_id = Number(studentId);
    }

    result.threshold = Number(threshold || 75);

    return result;
  };

  const handlePeriodChange = (value: string) => {
    setAcademicPeriodId(value);
    setClassId("");
    setExaminationId("");
    setStudentId("");
    setReportData(null);
    setReportGenerated(false);
  };

  const handleClassChange = (value: string) => {
    setClassId(value);
    setStudentId("");
    setReportData(null);
    setReportGenerated(false);
  };

  const generateReport = async () => {
    if (reportType === "student" && !studentId) {
      setError("Please select a student.");
      return;
    }

    if (loadingOptions) {
      setError("Please wait until the filter options finish loading.");
      return;
    }

    setLoading(true);
    setError("");
    setReportData(null);
    setReportGenerated(false);

    try {
      const filters = buildFilters();
      let response: unknown;

      switch (reportType) {
        case "overview":
          response = await getOverviewReport(filters);
          break;

        case "student":
          response = await getStudentReport(
            Number(studentId),
            filters
          );
          break;

        case "subjects":
          response = await getSubjectsReport(filters);
          break;

        case "classes":
          response = await getClassesReport(filters);
          break;

        case "attendance":
          response = await getAttendanceReport(filters);
          break;
      }

      setReportData(response);
      setReportGenerated(true);
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "Unable to generate the report.";

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (
    format: "excel" | "pdf"
  ) => {
    if (reportType === "student" && !studentId) {
      setError("Please select a student.");
      return;
    }

    setDownloading(true);
    setError("");

    try {
      const request = {
        report_type: reportType,
        ...buildFilters(),
      };

      const blob =
        format === "excel"
          ? await downloadExcelReport(request)
          : await downloadPdfReport(request);

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = `academic_${reportType}_report.${
        format === "excel" ? "xlsx" : "pdf"
      }`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : `Unable to download the ${format.toUpperCase()} report.`;

      setError(message);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="reports-page">
      <div className="reports-header">
        <div>
          <h1>Reports & Exports</h1>
          <p>
            Generate academic reports and download them
            in Excel or PDF format.
          </p>
        </div>
      </div>

      <div className="reports-layout">
        <div className="reports-panel">
          <div className="reports-panel-header">
            <h2>Generate Report</h2>
            <p>
              Select a report type and apply filters.
            </p>
          </div>

          <div className="reports-form">
            <div className="reports-field">
              <label htmlFor="reportType">
                Report Type
              </label>

              <select
                id="reportType"
                value={reportType}
                onChange={(event) => {
                  setReportType(
                    event.target.value as ReportType
                  );
                  setReportData(null);
                  setReportGenerated(false);
                  setError("");
                }}
              >
                {reportOptions.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                  >
                    {option.label}
                  </option>
                ))}
              </select>

              <small>
                {selectedReport?.description}
              </small>
            </div>

            <div className="reports-field">
              <label htmlFor="periodId">
                Academic Period
              </label>

              <select
                id="periodId"
                value={academicPeriodId}
                onChange={(event) =>
                  handlePeriodChange(event.target.value)
                }
                disabled={loadingOptions}
              >
                <option value="">All Academic Periods</option>

                {options.academic_periods.map((period) => (
                  <option
                    key={period.id}
                    value={period.id}
                  >
                    {period.name}
                    {period.is_active ? " (Active)" : ""}
                  </option>
                ))}
              </select>
            </div>

            {(reportType === "subjects" ||
              reportType === "attendance") && (
              <div className="reports-field">
                <label htmlFor="classId">
                  Class
                </label>

                <select
                  id="classId"
                  value={classId}
                  onChange={(event) =>
                    handleClassChange(event.target.value)
                  }
                  disabled={loadingOptions}
                >
                  <option value="">All Classes</option>

                  {options.classes.map((classroom) => {
                    const period = options.academic_periods.find(
                      (item) =>
                        item.id === classroom.academic_period_id
                    );

                    return (
                      <option
                        key={classroom.id}
                        value={classroom.id}
                      >
                        {classroom.label} - {period?.name ?? ""}
                      </option>
                    );
                  })}
                </select>
              </div>
            )}

            {(reportType === "subjects" ||
              reportType === "classes") && (
              <div className="reports-field">
                <label htmlFor="examinationId">
                  Examination
                </label>

                <select
                  id="examinationId"
                  value={examinationId}
                  onChange={(event) => {
                    setExaminationId(event.target.value);
                    setReportData(null);
                    setReportGenerated(false);
                  }}
                  disabled={loadingOptions}
                >
                  <option value="">All Examinations</option>

                  {options.examinations.map((exam) => (
                    <option
                      key={exam.id}
                      value={exam.id}
                    >
                      {exam.name} - {exam.exam_date}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {reportType === "student" && (
              <>
                <div className="reports-field">
                  <label htmlFor="studentClassId">
                    Class
                  </label>

                  <select
                    id="studentClassId"
                    value={classId}
                    onChange={(event) =>
                      handleClassChange(event.target.value)
                    }
                    disabled={loadingOptions}
                  >
                    <option value="">All Classes</option>

                    {options.classes.map((classroom) => {
                      const period = options.academic_periods.find(
                        (item) =>
                          item.id === classroom.academic_period_id
                      );

                      return (
                        <option
                          key={classroom.id}
                          value={classroom.id}
                        >
                          {classroom.label} - {period?.name ?? ""}
                        </option>
                      );
                    })}
                  </select>
                </div>

                <div className="reports-field">
                  <label htmlFor="studentId">
                    Student
                  </label>

                  <select
                    id="studentId"
                    value={studentId}
                    onChange={(event) =>
                      setStudentId(event.target.value)
                    }
                    disabled={loadingOptions}
                  >
                    <option value="">Select Student</option>

                    {options.students.map((student) => (
                      <option
                        key={student.id}
                        value={student.id}
                      >
                        {student.label}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            {reportType === "attendance" && (
              <div className="reports-field">
                <label htmlFor="threshold">
                  Attendance Threshold (%)
                </label>

                <input
                  id="threshold"
                  type="number"
                  min="0"
                  max="100"
                  value={threshold}
                  onChange={(event) =>
                    setThreshold(event.target.value)
                  }
                />
              </div>
            )}

            {selectedPeriod && (
              <small className="reports-filter-info">
                Selected academic period: {selectedPeriod.name}
              </small>
            )}

            {error && (
              <div className="reports-error">
                {error}
              </div>
            )}

            <button
              className="reports-generate-button"
              onClick={generateReport}
              disabled={loading || loadingOptions}
            >
              {loading
                ? "Generating..."
                : "Generate Report"}
            </button>
          </div>
        </div>

        <div className="reports-panel reports-download-panel">
          <h2>Export Report</h2>

          <p>
            Download your selected report in Excel or PDF format.
          </p>

          <div className="reports-export-actions">
            <button
              className="reports-excel-button"
              onClick={() => downloadReport("excel")}
              disabled={downloading || loadingOptions}
            >
              {downloading
                ? "Preparing..."
                : "Download Excel"}
            </button>

            <button
              className="reports-pdf-button"
              onClick={() => downloadReport("pdf")}
              disabled={downloading || loadingOptions}
            >
              {downloading
                ? "Preparing..."
                : "Download PDF"}
            </button>
          </div>

          <small>
            Select your filters before downloading the report.
          </small>
        </div>
      </div>

      {reportGenerated && (
        <div className="reports-panel reports-preview-panel">
          <div className="reports-preview-header">
            <div>
              <h2>Report Preview</h2>
              <p>{selectedReport?.label}</p>
            </div>

            <span className="reports-status">
              Generated
            </span>
          </div>

          <ReportResults data={reportData} />
        </div>
      )}
    </div>
  );
}

export default Reports;
