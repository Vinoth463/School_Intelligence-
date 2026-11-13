
import { useEffect, useState } from "react";
import {
  AlertTriangle,
  RefreshCw,
  TrendingDown,
} from "lucide-react";

import api from "../../services/api";

interface StudentDecline {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  academic_period_id: number;
  class_id: number;
  previous_examination_id: number;
  previous_examination_name: string;
  examination_id: number;
  examination_name: string;
  previous_percentage: number;
  current_percentage: number;
  percentage_change: number;
  performance_status: string;
}

interface SubjectDecline {
  student_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  previous_examination_name: string;
  examination_name: string;
  previous_percentage: number;
  current_percentage: number;
  percentage_change: number;
}

interface DecliningPerformanceProps {
  academicPeriodId?: number;
}

export default function DecliningPerformance({
  academicPeriodId,
}: DecliningPerformanceProps) {
  const [students, setStudents] = useState<StudentDecline[]>([]);
  const [subjects, setSubjects] = useState<SubjectDecline[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const loadDecliningPerformance = async () => {
      if (!academicPeriodId) {
        setStudents([]);
        setSubjects([]);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const [studentResponse, subjectResponse] = await Promise.all([
          api.get<StudentDecline[]>(
            "/analytics/declining-performance",
            {
              params: {
                academic_period_id: academicPeriodId,
                decline_threshold: 0,
              },
            }
          ),

          api.get<SubjectDecline[]>(
            "/analytics/declining-performance/subjects",
            {
              params: {
                academic_period_id: academicPeriodId,
              },
            }
          ),
        ]);

        if (active) {
          setStudents(studentResponse.data);
          setSubjects(subjectResponse.data);
        }
      } catch (err) {
        console.error("Failed to load declining performance:", err);

        if (active) {
          setError("Unable to load declining performance data.");
          setStudents([]);
          setSubjects([]);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    void loadDecliningPerformance();

    return () => {
      active = false;
    };
  }, [academicPeriodId]);

  const formatPercentage = (value: number) =>
    `${value.toFixed(2)}%`;

  const formatDecline = (value: number) =>
    `${Math.abs(value).toFixed(2)} percentage points`;

  return (
    <div className="declining-performance">
      <div className="analytics-panel-heading">
        <div>
          <h3>
            <TrendingDown size={19} />
            Declining Performance
          </h3>
          <p>
            Identify students and subjects with decreasing examination
            performance
          </p>
        </div>
      </div>

      {loading ? (
        <div className="analytics-loading">
          <RefreshCw className="loading-spinner" size={22} />
          <p>Loading declining performance...</p>
        </div>
      ) : error ? (
        <div className="analytics-error">
          <AlertTriangle size={18} />
          <p>{error}</p>
        </div>
      ) : (
        <>
          {/* Student performance declines */}
          <section className="analytics-panel">
            <div className="analytics-panel-heading">
              <div>
                <h3>Student Performance Declines</h3>
                <p>
                  Students whose overall examination performance has
                  decreased
                </p>
              </div>
            </div>

            <div className="analytics-table-wrapper">
              <table className="analytics-table">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Admission No.</th>
                    <th>Previous Exam</th>
                    <th>Current Exam</th>
                    <th>Previous</th>
                    <th>Current</th>
                    <th>Decline</th>
                  </tr>
                </thead>

                <tbody>
                  {students.map((item) => (
                    <tr
                      key={`${item.student_id}-${item.examination_id}`}
                    >
                      <td>
                        <strong>
                          {item.first_name} {item.last_name}
                        </strong>
                      </td>

                      <td>{item.admission_number}</td>

                      <td>{item.previous_examination_name}</td>

                      <td>{item.examination_name}</td>

                      <td>
                        {formatPercentage(item.previous_percentage)}
                      </td>

                      <td>
                        {formatPercentage(item.current_percentage)}
                      </td>

                      <td className="decline-value">
                        <strong>
                          {formatDecline(item.percentage_change)}
                        </strong>
                      </td>
                    </tr>
                  ))}

                  {students.length === 0 && (
                    <tr>
                      <td colSpan={7}>
                        No student performance declines found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Subject performance declines */}
          <section className="analytics-panel">
            <div className="analytics-panel-heading">
              <div>
                <h3>Subject Performance Declines</h3>
                <p>
                  Students whose marks have decreased in individual
                  subjects
                </p>
              </div>
            </div>

            <div className="analytics-table-wrapper">
              <table className="analytics-table">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Subject</th>
                    <th>Previous Exam</th>
                    <th>Current Exam</th>
                    <th>Previous</th>
                    <th>Current</th>
                    <th>Decline</th>
                  </tr>
                </thead>

                <tbody>
                  {subjects.map((item, index) => (
                    <tr
                      key={`${item.student_id}-${item.subject_id}-${index}`}
                    >
                      <td>
                        <strong>
                          {item.first_name} {item.last_name}
                        </strong>
                      </td>

                      <td>
                        <strong>{item.subject_name}</strong>
                        <span className="subject-code">
                          {item.subject_code}
                        </span>
                      </td>

                      <td>{item.previous_examination_name}</td>

                      <td>{item.examination_name}</td>

                      <td>
                        {formatPercentage(item.previous_percentage)}
                      </td>

                      <td>
                        {formatPercentage(item.current_percentage)}
                      </td>

                      <td className="decline-value">
                        <strong>
                          {formatDecline(item.percentage_change)}
                        </strong>
                      </td>
                    </tr>
                  ))}

                  {subjects.length === 0 && (
                    <tr>
                      <td colSpan={7}>
                        No subject performance declines found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
