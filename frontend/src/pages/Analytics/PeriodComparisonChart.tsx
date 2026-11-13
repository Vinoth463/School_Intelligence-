
import { useEffect, useState } from "react";
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
import { RefreshCw } from "lucide-react";

import analyticsService from "../../services/analytics";

interface PeriodResult {
  academic_period_id: number;
  academic_period_name: string;
  total_mark_records: number;
  students_evaluated: number;
  average_percentage: number;
  highest_percentage: number;
  lowest_percentage: number;
}

interface PeriodComparisonChartProps {
  classId?: number;
}

export default function PeriodComparisonChart({
  classId,
}: PeriodComparisonChartProps) {
  const [periods, setPeriods] = useState<PeriodResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let isActive = true;

    const loadComparison = async () => {
      try {
        setLoading(true);
        setError("");

        const result = await analyticsService.getPeriodComparison(classId);

        if (isActive) {
          setPeriods(result.periods as PeriodResult[]);
        }
      } catch (err) {
        console.error("Failed to load period comparison:", err);

        if (isActive) {
          setError("Unable to load academic period comparison.");
          setPeriods([]);
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
  }, [classId]);

  const chartData = periods.map((period) => ({
    period: period.academic_period_name,
    average: period.average_percentage,
    highest: period.highest_percentage,
    lowest: period.lowest_percentage,
  }));

  return (
    <section className="analytics-panel period-comparison-panel">
      <div className="analytics-panel-heading">
        <div>
          <h3>Academic Period Comparison</h3>
          <p>Compare academic performance across academic years</p>
        </div>
      </div>

      {loading ? (
        <div className="analytics-loading">
          <RefreshCw className="loading-spinner" size={22} />
          <p>Loading academic period comparison...</p>
        </div>
      ) : error ? (
        <div className="analytics-error">
          <p>{error}</p>
        </div>
      ) : periods.length === 0 ? (
        <div className="analytics-empty">
          No academic period comparison data available.
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
                  dataKey="period"
                  tick={{ fontSize: 12 }}
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

                <Legend />

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
                  <th>Academic Period</th>
                  <th>Students</th>
                  <th>Average</th>
                  <th>Highest</th>
                  <th>Lowest</th>
                </tr>
              </thead>

              <tbody>
                {periods.map((period) => (
                  <tr key={period.academic_period_id}>
                    <td>
                      <strong>{period.academic_period_name}</strong>
                    </td>
                    <td>{period.students_evaluated}</td>
                    <td>{period.average_percentage.toFixed(2)}%</td>
                    <td>{period.highest_percentage.toFixed(2)}%</td>
                    <td>{period.lowest_percentage.toFixed(2)}%</td>
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
