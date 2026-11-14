
import { useEffect, useState } from "react";
import {
  BrainCircuit,
  RefreshCw,
  Search,
  AlertCircle,
  CheckCircle2,
  TrendingUp,
  ShieldAlert,
  GraduationCap,
  CalendarDays,
  BookOpen,
  Users,
} from "lucide-react";

import predictionsService from "../../services/predictions";

import type {
  StudentOption,
  SubjectOption,
  ExaminationOption,
  UnderperformancePrediction,
} from "../../types/predictions";

import "./Predictions.css";

export default function Predictions() {
  const [students, setStudents] = useState<StudentOption[]>([]);
  const [subjects, setSubjects] = useState<SubjectOption[]>([]);
  const [examinations, setExaminations] = useState<ExaminationOption[]>([]);

  const [studentId, setStudentId] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [examinationId, setExaminationId] = useState("");

  const [studentSearch, setStudentSearch] = useState("");

  const [prediction, setPrediction] =
    useState<UnderperformancePrediction | null>(null);

  const [loadingOptions, setLoadingOptions] = useState(true);
  const [loadingExaminations, setLoadingExaminations] = useState(false);
  const [predicting, setPredicting] = useState(false);

  const [error, setError] = useState("");
  const [optionError, setOptionError] = useState("");

  // Load students and subjects.
  useEffect(() => {
    const loadOptions = async () => {
      try {
        setLoadingOptions(true);
        setOptionError("");

        const [studentData, subjectData] = await Promise.all([
          predictionsService.getStudents(),
          predictionsService.getSubjects(),
        ]);

        setStudents(studentData);
        setSubjects(subjectData);
      } catch (err) {
        console.error("Failed to load ML options:", err);
        setOptionError(
          "Unable to load students or subjects. Please refresh and try again."
        );
      } finally {
        setLoadingOptions(false);
      }
    };

    void loadOptions();
  }, []);

  // Load eligible examinations when student or subject changes.
  useEffect(() => {
    if (!studentId || !subjectId) {
      return;
    }

    let cancelled = false;

    const loadExaminations = async () => {
      try {
        setLoadingExaminations(true);
        setError("");
        setExaminations([]);
        setExaminationId("");
        setPrediction(null);

        const data = await predictionsService.getExaminations(
          Number(studentId),
          Number(subjectId)
        );

        if (!cancelled) {
          setExaminations(data);
        }
      } catch (err) {
        console.error("Failed to load examinations:", err);

        if (!cancelled) {
          setError(
            "Unable to load eligible examinations for this student and subject."
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingExaminations(false);
        }
      }
    };

    void loadExaminations();

    return () => {
      cancelled = true;
    };
  }, [studentId, subjectId]);

  const handleStudentChange = (value: string) => {
    setStudentId(value);
    setSubjectId("");
    setExaminationId("");
    setExaminations([]);
    setPrediction(null);
    setError("");
  };

  const handleSubjectChange = (value: string) => {
    setSubjectId(value);
    setExaminationId("");
    setExaminations([]);
    setPrediction(null);
    setError("");
  };

  const handlePrediction = async () => {
    if (!studentId || !subjectId || !examinationId) {
      setError("Please select a student, subject and examination.");
      return;
    }

    try {
      setPredicting(true);
      setError("");
      setPrediction(null);

      const result = await predictionsService.predict({
        student_id: Number(studentId),
        subject_id: Number(subjectId),
        target_examination_id: Number(examinationId),
      });

      setPrediction(result);
    } catch (err: unknown) {
      console.error("Prediction failed:", err);

      const apiError = err as {
        response?: {
          data?: {
            detail?: unknown;
          };
        };
      };

      const detail = apiError.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Unable to generate prediction. Please try again."
      );
} finally {
      setPredicting(false);
    }
  };

  const filteredStudents = students.filter((student) => {
    const search = studentSearch.toLowerCase().trim();

    return (
      student.name.toLowerCase().includes(search) ||
      student.admission_number.toLowerCase().includes(search)
    );
  });

  const selectedStudent = students.find(
    (student) => String(student.id) === studentId
  );

  const selectedSubject = subjects.find(
    (subject) => String(subject.id) === subjectId
  );

  const selectedExamination = examinations.find(
    (exam) => String(exam.id) === examinationId
  );

  const getRiskClass = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "high":
        return "high";
      case "medium":
        return "medium";
      case "low":
        return "low";
      default:
        return "unknown";
    }
  };

  const formatPercentage = (value: number | null | undefined) => {
    if (value === null || value === undefined || !Number.isFinite(value)) {
      return "—";
    }

    return `${value.toFixed(2)}%`;
  };

  if (loadingOptions) {
    return (
      <div className="predictions-loading">
        <RefreshCw className="predictions-spinner" size={25} />
        <p>Loading prediction options...</p>
      </div>
    );
  }

  return (
    <div className="predictions-page">
      {/* Page heading */}
      <div className="predictions-heading">
        <div>
          <h1>ML Performance Predictions</h1>
          <p>
            Identify students who may need additional academic support
            using machine learning.
          </p>
        </div>

        <div className="predictions-heading-icon">
          <BrainCircuit size={25} />
          <span>Random Forest ML</span>
        </div>
      </div>

      {/* Option loading error */}
      {optionError && (
        <div className="predictions-error">
          <AlertCircle size={19} />
          <p>{optionError}</p>
        </div>
      )}

      {/* Prediction filters */}
      <section className="predictions-panel">
        <div className="predictions-panel-heading">
          <div className="predictions-section-icon">
            <Search size={19} />
          </div>

          <div>
            <h3>Configure Prediction</h3>
            <p>Select the student, subject and future examination.</p>
          </div>
        </div>

        <div className="predictions-filter-grid">
          {/* Student */}
          <div className="predictions-field">
            <label htmlFor="prediction-student">Student</label>

            <div className="predictions-search-wrapper">
              <Search size={15} />

              <input
                type="text"
                placeholder="Search student or admission number"
                value={studentSearch}
                onChange={(event) => setStudentSearch(event.target.value)}
                disabled={Boolean(studentId)}
              />
            </div>

            <select
              id="prediction-student"
              value={studentId}
              onChange={(event) => handleStudentChange(event.target.value)}
            >
              <option value="">Select student</option>

              {filteredStudents.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.name} ({student.admission_number})
                </option>
              ))}
            </select>

            {studentId && (
              <button
                type="button"
                className="predictions-clear-selection"
                onClick={() => {
                  setStudentSearch("");
                  handleStudentChange("");
                }}
              >
                Change student
              </button>
            )}
          </div>

          {/* Subject */}
          <div className="predictions-field">
            <label htmlFor="prediction-subject">Subject</label>

            <select
              id="prediction-subject"
              value={subjectId}
              onChange={(event) => handleSubjectChange(event.target.value)}
              disabled={!studentId}
            >
              <option value="">Select subject</option>

              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.name} ({subject.code})
                </option>
              ))}
            </select>
          </div>

          {/* Examination */}
          <div className="predictions-field">
            <label htmlFor="prediction-examination">
              Target Examination
            </label>

            <select
              id="prediction-examination"
              value={examinationId}
              onChange={(event) => {
                setExaminationId(event.target.value);
                setPrediction(null);
                setError("");
              }}
              disabled={!subjectId || loadingExaminations}
            >
              <option value="">
                {loadingExaminations
                  ? "Loading examinations..."
                  : "Select examination"}
              </option>

              {examinations.map((exam) => (
                <option key={exam.id} value={exam.id}>
                  {exam.name} — {exam.exam_date}
                </option>
              ))}
            </select>

            {loadingExaminations && (
              <span className="predictions-field-hint">
                Loading eligible examinations...
              </span>
            )}

            {!loadingExaminations &&
              studentId &&
              subjectId &&
              examinations.length === 0 && (
                <span className="predictions-field-hint">
                  No eligible future examinations found.
                </span>
              )}
          </div>
        </div>

        {/* Selected information */}
        {selectedStudent && selectedSubject && (
          <div className="predictions-selection-summary">
            <span>
              <Users size={15} />
              {selectedStudent.name}
            </span>

            <span>
              <BookOpen size={15} />
              {selectedSubject.name}
            </span>

            {selectedExamination && (
              <span>
                <CalendarDays size={15} />
                {selectedExamination.name}
              </span>
            )}
          </div>
        )}

        <div className="predictions-action">
          <button
            type="button"
            className="predictions-run-button"
            onClick={() => void handlePrediction()}
            disabled={
              !studentId ||
              !subjectId ||
              !examinationId ||
              predicting ||
              loadingExaminations
            }
          >
            {predicting ? (
              <>
                <RefreshCw className="predictions-spinner" size={17} />
                Generating Prediction...
              </>
            ) : (
              <>
                <BrainCircuit size={18} />
                Run Prediction
              </>
            )}
          </button>
        </div>
      </section>

      {/* Error */}
      {error && (
        <div className="predictions-error">
          <AlertCircle size={19} />
          <p>{error}</p>
        </div>
      )}

      {/* Prediction results */}
      {prediction && (
        <div className="predictions-results">
          <div className="predictions-result-heading">
            <div>
              <h2>Prediction Results</h2>
              <p>
                Machine learning assessment for the selected student.
              </p>
            </div>

            <span className="predictions-model-label">
              <BrainCircuit size={15} />
              {prediction.model_name}
            </span>
          </div>

          {/* Main result */}
          <section className="predictions-panel">
            <div className="predictions-result-main">
              <div>
                <span className="predictions-result-label">
                  Underperformance Assessment
                </span>

                <h2
                  className={
                    prediction.predicted_underperformance
                      ? "prediction-negative"
                      : "prediction-positive"
                  }
                >
                  {prediction.predicted_underperformance
                    ? "Potential Underperformance"
                    : "No Underperformance Predicted"}
                </h2>

                <p>
                  {prediction.score_interpretation}
                </p>
              </div>

              <div
                className={`predictions-risk-badge ${getRiskClass(
                  prediction.risk_category
                )}`}
              >
                <ShieldAlert size={20} />
                <span>
                  {prediction.risk_category} Risk
                </span>
              </div>
            </div>

            <div className="predictions-score-section">
              <div className="predictions-score-heading">
                <span>Model Score</span>
                <strong>
                  {(prediction.underperformance_score * 100).toFixed(2)}%
                </strong>
              </div>

              <div className="predictions-score-track">
                <div
                  className={`predictions-score-fill ${getRiskClass(
                    prediction.risk_category
                  )}`}
                  style={{
                    width: `${Math.max(
                      0,
                      Math.min(100, prediction.underperformance_score * 100)
                    )}%`,
                  }}
                />
              </div>

              <p>
                Classification threshold:{" "}
                {(prediction.classification_threshold * 100).toFixed(0)}%
              </p>
            </div>
          </section>

          {/* Historical performance */}
          <section className="predictions-panel">
            <div className="predictions-panel-heading">
              <div className="predictions-section-icon">
                <TrendingUp size={19} />
              </div>

              <div>
                <h3>Historical Academic Features</h3>
                <p>Information used by the prediction model.</p>
              </div>
            </div>

            <div className="predictions-feature-grid">
              <div className="predictions-feature-card">
                <span>Previous Exam Score</span>
                <strong>
                  {formatPercentage(
                    prediction.features.previous_exam_percentage
                  )}
                </strong>
              </div>

              <div className="predictions-feature-card">
                <span>Historical Average</span>
                <strong>
                  {formatPercentage(
                    prediction.features.historical_average_percentage
                  )}
                </strong>
              </div>

              <div className="predictions-feature-card">
                <span>Marks Trend</span>
                <strong>
                  {prediction.features.marks_trend === null
                    ? "—"
                    : `${prediction.features.marks_trend > 0 ? "+" : ""}${prediction.features.marks_trend.toFixed(2)} pts`}
                </strong>
              </div>

              <div className="predictions-feature-card">
                <span>Attendance</span>
                <strong>
                  {formatPercentage(
                    prediction.features.attendance_percentage
                  )}
                </strong>
              </div>

              <div className="predictions-feature-card">
                <span>Previous Examinations</span>
                <strong>
                  {prediction.historical_examination_count}
                </strong>
              </div>

              <div className="predictions-feature-card">
                <span>Attendance Sessions</span>
                <strong>
                  {prediction.historical_attendance_sessions}
                </strong>
              </div>

              <div className="predictions-feature-card">
                <span>Recent 60-Day Attendance</span>
                <strong>
                  {formatPercentage(
                    prediction.features.attendance_recent_60d
                  )}
                </strong>
              </div>

              <div className="predictions-feature-card">
                <span>Class</span>
                <strong>
                  {prediction.features.class_grade}
                </strong>
              </div>
            </div>
          </section>

          {/* Indicators */}
          <div className="predictions-indicator-grid">
            <section className="predictions-panel">
              <div className="predictions-panel-heading">
                <div className="predictions-indicator-icon warning">
                  <AlertCircle size={19} />
                </div>

                <div>
                  <h3>Risk Indicators</h3>
                  <p>Factors requiring academic attention.</p>
                </div>
              </div>

              {prediction.risk_indicators.length > 0 ? (
                <ul className="predictions-indicator-list">
                  {prediction.risk_indicators.map((item, index) => (
                    <li key={index}>
                      <AlertCircle size={16} />
                      {item}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="predictions-no-indicators">
                  No risk indicators identified.
                </p>
              )}
            </section>

            <section className="predictions-panel">
              <div className="predictions-panel-heading">
                <div className="predictions-indicator-icon success">
                  <CheckCircle2 size={19} />
                </div>

                <div>
                  <h3>Positive Indicators</h3>
                  <p>Positive academic observations.</p>
                </div>
              </div>

              {prediction.positive_indicators.length > 0 ? (
                <ul className="predictions-indicator-list positive-list">
                  {prediction.positive_indicators.map((item, index) => (
                    <li key={index}>
                      <CheckCircle2 size={16} />
                      {item}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="predictions-no-indicators">
                  No positive indicators identified.
                </p>
              )}
            </section>
          </div>

          {/* Data sufficiency */}
          <section className="predictions-panel">
            <div className="predictions-panel-heading">
              <div className="predictions-section-icon">
                <GraduationCap size={19} />
              </div>

              <div>
                <h3>Data Sufficiency</h3>
                <p>Availability of historical data used for this assessment.</p>
              </div>
            </div>

            <div className="predictions-data-status">
              <strong>
                {prediction.data_sufficiency_status.replaceAll("_", " ")}
              </strong>

              <span>
                {prediction.data_type}
              </span>
            </div>

            {prediction.data_sufficiency_warnings.length > 0 ? (
              <ul className="predictions-warning-list">
                {prediction.data_sufficiency_warnings.map((warning, index) => (
                  <li key={index}>{warning}</li>
                ))}
              </ul>
            ) : (
              <p className="predictions-no-indicators">
                No data sufficiency warnings.
              </p>
            )}
          </section>
        </div>
      )}

      {/* Initial empty state */}
      {!prediction && !error && (
        <div className="predictions-empty">
          <div className="predictions-empty-icon">
            <BrainCircuit size={34} />
          </div>

          <h3>Ready to Analyze Student Performance</h3>

          <p>
            Select a student, subject and future examination, then run
            the machine learning model to view the prediction.
          </p>
        </div>
      )}
    </div>
  );
}
