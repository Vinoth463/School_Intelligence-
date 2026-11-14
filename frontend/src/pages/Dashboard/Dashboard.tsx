
import { useCallback, useEffect, useState } from "react";
import {
  Users,
  GraduationCap,
  ClipboardCheck,
  FileSpreadsheet,
  RefreshCw,
  AlertCircle,
} from "lucide-react";

import dashboardService from "../../services/dashboard";
import type { DashboardOverview } from "../../types/dashboard";
import "./Dashboard.css";

interface StatCardProps {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

function StatCard({
  title,
  value,
  description,
  icon,
  color,
}: StatCardProps) {
  return (
    <div className="dashboard-stat-card">
      <div className="stat-card-top">
        <span className="stat-title">{title}</span>
        <div className={`stat-icon ${color}`}>{icon}</div>
      </div>

      <h2 className="stat-value">{value}</h2>
      <p className="stat-description">{description}</p>
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async () => {
    try {
      setError("");
      setIsLoading(true);

      const response = await dashboardService.getOverview();
      setData(response);
    } catch {
      setError("Unable to load dashboard data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
  // Load dashboard data when the component mounts.
  // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadDashboard();
  }, [loadDashboard]);

  if (isLoading && !data) {
    return (
      <div className="dashboard-loading">
        <RefreshCw className="loading-icon" size={28} />
        <p>Loading academic dashboard...</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="dashboard-error">
        <AlertCircle size={28} />
        <h3>Dashboard unavailable</h3>
        <p>{error}</p>
        <button onClick={() => void loadDashboard()}>
          Try Again
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <span className="dashboard-eyebrow">ACADEMIC OVERVIEW</span>
          <h1>Dashboard</h1>
          <p>Monitor your institution's academic performance.</p>
        </div>

        <button
          className="refresh-button"
          onClick={() => void loadDashboard()}
          disabled={isLoading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="dashboard-inline-error" role="alert">
          {error} Showing the last successfully loaded data.
        </div>
      )}

      <div className="dashboard-stats-grid">
        <StatCard
          title="Total Students"
          value={data.total_students.toLocaleString("en-IN")}
          description="Registered students"
          icon={<Users size={21} />}
          color="blue"
        />

        <StatCard
          title="Average Performance"
          value={`${data.average_performance_percentage.toFixed(2)}%`}
          description="Overall academic average"
          icon={<GraduationCap size={21} />}
          color="green"
        />

        <StatCard
          title="Attendance Rate"
          value={`${data.attendance_percentage.toFixed(2)}%`}
          description="Present attendance sessions"
          icon={<ClipboardCheck size={21} />}
          color="purple"
        />

        <StatCard
          title="Mark Records"
          value={data.total_mark_records.toLocaleString("en-IN")}
          description="Recorded academic marks"
          icon={<FileSpreadsheet size={21} />}
          color="orange"
        />
      </div>

      <div className="dashboard-section-grid">
        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <h2>Academic Performance</h2>
              <p>Overall institution performance</p>
            </div>
            <GraduationCap size={21} />
          </div>

          <div className="performance-content">
            <div className="performance-circle">
              <div>
                <strong>
                  {data.average_performance_percentage.toFixed(2)}%
                </strong>
                <span>Average</span>
              </div>
            </div>

            <div className="performance-details">
              <h3>Academic Summary</h3>
              <p>
                The institution's current overall academic performance
                average is {data.average_performance_percentage.toFixed(2)}%.
              </p>
            </div>
          </div>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <h2>Attendance Summary</h2>
              <p>Institution attendance overview</p>
            </div>
            <ClipboardCheck size={21} />
          </div>

          <div className="attendance-details">
            <div className="attendance-item">
              <span>Total Sessions</span>
              <strong>
                {data.total_attendance_sessions.toLocaleString("en-IN")}
              </strong>
            </div>

            <div className="attendance-item">
              <span>Present Sessions</span>
              <strong>
                {data.present_attendance_sessions.toLocaleString("en-IN")}
              </strong>
            </div>

            <div className="attendance-item">
              <span>Absent Sessions</span>
              <strong>
                {(
                  data.total_attendance_sessions -
                  data.present_attendance_sessions
                ).toLocaleString("en-IN")}
              </strong>
            </div>

            <div className="attendance-progress">
              <div className="progress-header">
                <span>Attendance Percentage</span>
                <strong>{data.attendance_percentage.toFixed(2)}%</strong>
              </div>

              <div
                className="progress-track"
                role="progressbar"
                aria-valuenow={data.attendance_percentage}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label="Attendance percentage"
              >
                <div
                  className="progress-fill"
                  style={{
                    width: `${Math.min(
                      100,
                      Math.max(0, data.attendance_percentage)
                    )}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </section>
      </div>

      <div className="dashboard-bottom-info">
        <span>
          Institution ID: {data.institution_id}
        </span>

        <span>
          {data.academic_period_id
            ? `Academic Period ID: ${data.academic_period_id}`
            : "All Academic Periods"}
        </span>
      </div>
    </div>
  );
}
