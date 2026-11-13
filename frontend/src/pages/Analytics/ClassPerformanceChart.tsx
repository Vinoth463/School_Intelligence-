
import {
  BarChart,
  Bar,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ClassPerformance } from "../../types/analytics";

interface ClassPerformanceChartProps {
  classes: ClassPerformance[];
}

export default function ClassPerformanceChart({
  classes,
}: ClassPerformanceChartProps) {
  const chartData = classes.map((item) => ({
    className: `${item.grade}-${item.section}`,
    average: item.average_percentage,
    students: item.students_evaluated,
  }));

  if (classes.length === 0) {
    return (
      <section className="analytics-panel">
        <div className="analytics-panel-heading">
          <div>
            <h3>Class Performance</h3>
            <p>Average academic performance by class</p>
          </div>
        </div>

        <div className="analytics-empty">
          No class performance data available.
        </div>
      </section>
    );
  }

  return (
    <section className="analytics-panel class-performance-panel">
      <div className="analytics-panel-heading">
        <div>
          <h3>Class Performance</h3>
          <p>Average academic performance across classes</p>
        </div>
      </div>

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
              dataKey="className"
              tick={{ fontSize: 12 }}
            />

            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12 }}
            />

            <Tooltip
              formatter={(value) => [
                `${Number(value).toFixed(2)}%`,
                "Average Performance",
              ]}
            />

            <Bar
              dataKey="average"
              name="Average Performance"
              fill="#5267c5"
              radius={[6, 6, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="analytics-table-wrapper">
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Class</th>
              <th>Students Evaluated</th>
              <th>Average</th>
              <th>Highest</th>
              <th>Lowest</th>
            </tr>
          </thead>

          <tbody>
            {classes.map((item) => (
              <tr key={item.class_id}>
                <td>
                  <strong>
                    {item.grade} - {item.section}
                  </strong>
                </td>
                <td>{item.students_evaluated}</td>
                <td>{item.average_percentage.toFixed(2)}%</td>
                <td>{item.highest_percentage.toFixed(2)}%</td>
                <td>{item.lowest_percentage.toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
