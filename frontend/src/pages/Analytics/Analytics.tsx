
import { useCallback, useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  BookOpen,
  Users,
  TrendingUp,
  Award,
  RefreshCw,
  Filter,
} from "lucide-react";

import analyticsService from "../../services/analytics";
import ClassPerformanceChart from "./ClassPerformanceChart";
import ExaminationComparisonChart from "./ExaminationComparisonChart";
import PeriodComparisonChart from "./PeriodComparisonChart";
import DecliningPerformance from "./DecliningPerformance";

import type {
  SubjectAnalytics,
  PeriodOption,
  ExaminationOption,
  ClassPerformance,
} from "../../types/analytics";

import "./Analytics.css";

export default function Analytics() {
  const [subjects, setSubjects] = useState<SubjectAnalytics[]>([]);
  const [periods, setPeriods] = useState<PeriodOption[]>([]);
  const [examinations, setExaminations] = useState<ExaminationOption[]>([]);
  const [classes, setClasses] = useState<ClassPerformance[]>([]);

  const [periodId, setPeriodId] = useState("");
  const [examinationId, setExaminationId] = useState("");
  const [classId, setClassId] = useState("");

  const [loadingPeriods, setLoadingPeriods] = useState(true);
  const [loadingOptions, setLoadingOptions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load available academic periods.
  useEffect(() => {
    const loadPeriods = async () => {
      try {
        setLoadingPeriods(true);

        const result = await analyticsService.getPeriodComparison();

        setPeriods(result.periods);

        if (result.periods.length > 0) {
          const latestPeriod = result.periods[result.periods.length - 1];
          setPeriodId(String(latestPeriod.academic_period_id));
        }
      } catch (err) {
        console.error("Failed to load academic periods:", err);
        setError("Unable to load academic periods.");
      } finally {
        setLoadingPeriods(false);
      }
    };

    void loadPeriods();
  }, []);

  // Load classes and examinations when academic period changes.
  useEffect(() => {
    if (!periodId) return;

    const loadFilterOptions = async () => {
      try {
        setLoadingOptions(true);
        setError("");

        setClasses([]);
        setExaminations([]);

        const selectedPeriod = Number(periodId);

        const [classData, examinationData] = await Promise.all([
          analyticsService.getClassPerformance(selectedPeriod),
          analyticsService.getExaminationComparison(selectedPeriod),
        ]);

        setClasses(classData);
        setExaminations(examinationData.examinations);
      } catch (err) {
        console.error("Failed to load analytics filters:", err);
        setError("Unable to load classes or examinations.");
      } finally {
        setLoadingOptions(false);
      }
    };

    void loadFilterOptions();
  }, [periodId]);

  // Load subject analytics whenever filters change.
  const fetchAnalytics = useCallback(async () => {
    if (!periodId) return;

    try {
      setLoading(true);
      setError("");

      const data = await analyticsService.getSubjectAnalytics({
        academic_period_id: Number(periodId),
        examination_id: examinationId
          ? Number(examinationId)
          : undefined,
        class_id: classId ? Number(classId) : undefined,
      });

      setSubjects(data);
    } catch (err) {
      console.error("Failed to load subject analytics:", err);
      setError("Unable to load academic analytics. Please try again.");
      setSubjects([]);
    } finally {
      setLoading(false);
    }
  }, [periodId, examinationId, classId]);

useEffect(() => {
  // Fetch remote analytics whenever the selected filters change.
  // State updates occur after the asynchronous API request.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  void fetchAnalytics();
}, [fetchAnalytics]);

  const handlePeriodChange = (value: string) => {
    setPeriodId(value);
    setExaminationId("");
    setClassId("");
  };

  const averagePerformance =
    subjects.length > 0
      ? subjects.reduce(
          (total, subject) => total + subject.average_percentage,
          0
        ) / subjects.length
      : 0;

  const totalStudents = subjects.reduce(
    (maximum, subject) =>
      Math.max(maximum, subject.students_evaluated),
    0
  );

  const highestSubject = subjects.reduce<SubjectAnalytics | null>(
    (highest, subject) =>
      !highest || subject.average_percentage > highest.average_percentage
        ? subject
        : highest,
    null
  );

  const gradeData = subjects.map((subject) => ({
    subject: subject.subject_code,
    A: subject.grade_a_count,
    B: subject.grade_b_count,
    C: subject.grade_c_count,
    D: subject.grade_d_count,
    E: subject.grade_e_count,
    F: subject.grade_f_count,
  }));

  if (loadingPeriods) {
    return (
      <div className="analytics-loading">
        <RefreshCw className="loading-spinner" size={24} />
        <p>Loading academic periods...</p>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <div className="analytics-heading">
        <div>
          <h1>Academic Analytics</h1>
          <p>
            Analyze subject performance and grade distribution across
            your institution.
          </p>
        </div>

        <button
          className="analytics-refresh"
          onClick={() => void fetchAnalytics()}
          disabled={loading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Analytics filters */}
      <section className="analytics-filters">
        <div className="analytics-filter-heading">
          <Filter size={18} />
          <h3>Filter Analytics</h3>
        </div>

        <div className="analytics-filter-grid">
          <div className="analytics-filter-field">
            <label htmlFor="academic-period">Academic Period</label>
            <select
              id="academic-period"
              value={periodId}
              onChange={(event) => handlePeriodChange(event.target.value)}
            >
              <option value="">Select academic period</option>

              {periods.map((period) => (
                <option
                  key={period.academic_period_id}
                  value={period.academic_period_id}
                >
                  {period.academic_period_name}
                </option>
              ))}
            </select>
          </div>

          <div className="analytics-filter-field">
            <label htmlFor="examination">Examination</label>
            <select
              id="examination"
              value={examinationId}
              onChange={(event) => setExaminationId(event.target.value)}
              disabled={loadingOptions || !periodId}
            >
              <option value="">All Examinations</option>

              {examinations.map((examination) => (
                <option
                  key={examination.examination_id}
                  value={examination.examination_id}
                >
                  {examination.examination_name}
                </option>
              ))}
            </select>
          </div>

          <div className="analytics-filter-field">
            <label htmlFor="school-class">Class</label>
            <select
              id="school-class"
              value={classId}
              onChange={(event) => setClassId(event.target.value)}
              disabled={loadingOptions || !periodId}
            >
              <option value="">All Classes</option>

              {classes.map((schoolClass) => (
                <option
                  key={schoolClass.class_id}
                  value={schoolClass.class_id}
                >
                  {schoolClass.grade} - {schoolClass.section}
                </option>
              ))}
            </select>
          </div>
        </div>

        {loadingOptions && (
          <p className="analytics-filter-status">
            Loading filter options...
          </p>
        )}
      </section>

      {error && (
        <div className="analytics-error">
          <p>{error}</p>
          <button onClick={() => void fetchAnalytics()}>
            Try Again
          </button>
        </div>
      )}

      {loading ? (
        <div className="analytics-loading">
          <RefreshCw className="loading-spinner" size={24} />
          <p>Loading subject analytics...</p>
        </div>
      ) : !error && subjects.length === 0 ? (
        <div className="analytics-empty">
          No subject analytics data is available for these filters.
        </div>
      ) : !error ? (
        <>
          {/* KPI cards */}
          <div className="analytics-stats">
            <div className="analytics-stat-card">
              <div className="analytics-stat-icon blue">
                <BookOpen size={21} />
              </div>
              <div>
                <span>Total Subjects</span>
                <h2>{subjects.length}</h2>
              </div>
            </div>

            <div className="analytics-stat-card">
              <div className="analytics-stat-icon purple">
                <Users size={21} />
              </div>
              <div>
                <span>Students Evaluated</span>
                <h2>{totalStudents}</h2>
              </div>
            </div>

            <div className="analytics-stat-card">
              <div className="analytics-stat-icon green">
                <TrendingUp size={21} />
              </div>
              <div>
                <span>Average Performance</span>
                <h2>{averagePerformance.toFixed(2)}%</h2>
              </div>
            </div>

            <div className="analytics-stat-card">
              <div className="analytics-stat-icon orange">
                <Award size={21} />
              </div>
              <div>
                <span>Top Performing Subject</span>
                <h2 className="analytics-top-subject">
                  {highestSubject?.subject_code ?? "—"}
                </h2>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="analytics-chart-grid">
            <section className="analytics-panel">
              <div className="analytics-panel-heading">
                <div>
                  <h3>Subject Performance</h3>
                  <p>Average percentage by subject</p>
                </div>
              </div>

              <div className="analytics-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={subjects}
                    margin={{ top: 15, right: 10, left: -15, bottom: 5 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />
                    <XAxis dataKey="subject_code" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <Tooltip
                      formatter={(value) => [
                        `${Number(value).toFixed(2)}%`,
                        "Average",
                      ]}
                    />
                    <Bar
                      dataKey="average_percentage"
                      name="Average Performance"
                      fill="#5267c5"
                      radius={[6, 6, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="analytics-panel">
              <div className="analytics-panel-heading">
                <div>
                  <h3>Grade Distribution</h3>
                  <p>Number of students in each grade</p>
                </div>
              </div>

              <div className="analytics-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={gradeData}
                    margin={{ top: 15, right: 10, left: -15, bottom: 5 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />
                    <XAxis dataKey="subject" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="A" stackId="grades" fill="#269b72" />
                    <Bar dataKey="B" stackId="grades" fill="#65b98c" />
                    <Bar dataKey="C" stackId="grades" fill="#e3b64e" />
                    <Bar dataKey="D" stackId="grades" fill="#e58b45" />
                    <Bar dataKey="E" stackId="grades" fill="#df6c62" />
                    <Bar dataKey="F" stackId="grades" fill="#bd4c59" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
                <ClassPerformanceChart classes={classes} />

                {/* Examination Comparison */}
                {periodId && (
                <ExaminationComparisonChart
                    academicPeriodId={Number(periodId)}
                    classId={classId ? Number(classId) : undefined}
                />
                )}

                {/* Academic Period Comparison */}
                <PeriodComparisonChart
                classId={classId ? Number(classId) : undefined}
                />

                {/* Declining Performance */}
                <DecliningPerformance
                academicPeriodId={periodId ? Number(periodId) : undefined}
                />
                

          {/* Subject details */}
          <section className="analytics-panel analytics-table-panel">
            <div className="analytics-panel-heading">
              <div>
                <h3>Subject Performance Details</h3>
                <p>Detailed academic statistics for each subject</p>
              </div>
            </div>

            <div className="analytics-table-wrapper">
              <table className="analytics-table">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Students</th>
                    <th>Average</th>
                    <th>Highest</th>
                    <th>Lowest</th>
                    <th>Grade A</th>
                    <th>Grade F</th>
                  </tr>
                </thead>

                <tbody>
                  {subjects.map((subject) => (
                    <tr key={subject.subject_id}>
                      <td>
                        <strong>{subject.subject_name}</strong>
                        <span className="subject-code">
                          {subject.subject_code}
                        </span>
                      </td>
                      <td>{subject.students_evaluated}</td>
                      <td>
                        <strong>
                          {subject.average_percentage.toFixed(2)}%
                        </strong>
                      </td>
                      <td>{subject.highest_percentage.toFixed(2)}%</td>
                      <td>{subject.lowest_percentage.toFixed(2)}%</td>
                      <td>{subject.grade_a_count}</td>
                      <td>{subject.grade_f_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
