
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { RefreshCw } from "lucide-react";

import analyticsService from "../../services/analytics";

interface ExaminationResult {
  examination_id: number;
  examination_name: string;
  exam_date: string;
  total_mark_records: number;
  students_evaluated: number;
  average_percentage: number;
  highest_percentage: number;
  lowest_percentage: number;
}

interface ExaminationComparisonChartProps {
  academicPeriodId: number;
  classId?: number;
}

export default function ExaminationComparisonChart({
  academicPeriodId,
  classId,
}: ExaminationComparisonChartProps) {
  const [examinations, setExaminations] = useState<ExaminationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let isActive = true;

    const loadComparison = async () => {
      try {
        setLoading(true);
        setError("");

        const result = await analyticsService.getExaminationComparison(
          academicPeriodId,
          classId
        );

        if (isActive) {
          setExaminations(
            result.examinations as ExaminationResult[]
          );
        }
      } catch (err) {
        console.error("Failed to load examination comparison:", err);

        if (isActive) {
          setError("Unable to load examination comparison.");
          setExaminations([]);
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    void loadComparison();

    return () => {
      isActive = false;
    };
  }, [academicPeriodId, classId]);

  const chartData = examinations.map((exam) => ({
    examination: exam.examination_name,
    average: exam.average_percentage,
    highest: exam.highest_percentage,
    lowest: exam.lowest_percentage,
  }));

  return (
    <section className="analytics-panel examination-comparison-panel">
      <div className="analytics-panel-heading">
        <div>
          <h3>Examination Comparison</h3>
          <p>Compare average performance across examinations</p>
        </div>
      </div>

      {loading ? (
        <div className="analytics-loading">
          <RefreshCw className="loading-spinner" size={22} />
          <p>Loading examination comparison...</p>
        </div>
      ) : error ? (
        <div className="analytics-error">
          <p>{error}</p>
        </div>
      ) : examinations.length === 0 ? (
        <div className="analytics-empty">
          No examination comparison data available.
        </div>
      ) : (
        <>
          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 15, right: 15, left: -15, bottom: 5 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />

                <XAxis
                  dataKey="examination"
                  tick={{ fontSize: 11 }}
                />

                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 12 }}
                />

                <Tooltip
                  formatter={(value) => [
                    `${Number(value).toFixed(2)}%`,
                    "Performance",
                  ]}
                />

                <Bar
                  dataKey="average"
                  name="Average"
                  fill="#5267c5"
                  radius={[6, 6, 0, 0]}
                />

                <Bar
                  dataKey="highest"
                  name="Highest"
                  fill="#269b72"
                  radius={[6, 6, 0, 0]}
                />

                <Bar
                  dataKey="lowest"
                  name="Lowest"
                  fill="#e58b45"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="analytics-table-wrapper">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Examination</th>
                  <th>Date</th>
                  <th>Students</th>
                  <th>Average</th>
                  <th>Highest</th>
                  <th>Lowest</th>
                </tr>
              </thead>

              <tbody>
                {examinations.map((exam) => (
                  <tr key={exam.examination_id}>
                    <td>
                      <strong>{exam.examination_name}</strong>
                    </td>
                    <td>{exam.exam_date}</td>
                    <td>{exam.students_evaluated}</td>
                    <td>{exam.average_percentage.toFixed(2)}%</td>
                    <td>{exam.highest_percentage.toFixed(2)}%</td>
                    <td>{exam.lowest_percentage.toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
