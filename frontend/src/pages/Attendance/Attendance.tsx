
import { useEffect, useState } from "react";
import attendanceService from "../../services/attendance";

import type {
  StudentAttendance,
  SubjectAttendance,
  ClassAttendance,
  LowAttendanceStudent,
  StudentSubjectAttendance,
  AcademicPeriodAttendanceComparison,
} from "../../types/attendance";

import "./Attendance.css";

const Attendance = () => {
  const [periods, setPeriods] = useState<
    AcademicPeriodAttendanceComparison[]
  >([]);

  const [selectedPeriod, setSelectedPeriod] = useState<number | "">("");
  const [selectedClass, setSelectedClass] = useState<number | "">("");

  const [students, setStudents] = useState<StudentAttendance[]>([]);
  const [subjects, setSubjects] = useState<SubjectAttendance[]>([]);
  const [classes, setClasses] = useState<ClassAttendance[]>([]);
  const [lowAttendance, setLowAttendance] = useState<
    LowAttendanceStudent[]
  >([]);
  const [studentSubjects, setStudentSubjects] = useState<
    StudentSubjectAttendance[]
  >([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load available academic periods.
  useEffect(() => {
    const loadPeriods = async () => {
      try {
        setError("");

        const data =
          await attendanceService.getAcademicPeriodComparison();

        setPeriods(data);

        if (data.length > 0) {
          setSelectedPeriod(data[0].academic_period_id);
        }
      } catch (err) {
        console.error("Failed to load academic periods:", err);
        setError("Unable to load academic periods.");
      }
    };

    loadPeriods();
  }, []);

  // Load attendance data whenever filters change.
  useEffect(() => {
    if (selectedPeriod === "") return;

    const loadAttendance = async () => {
      setLoading(true);
      setError("");

      const params: {
        academic_period_id: number;
        class_id?: number;
      } = {
        academic_period_id: selectedPeriod,
      };

      if (selectedClass !== "") {
        params.class_id = selectedClass;
      }

      try {
        const [
          studentData,
          subjectData,
          classData,
          lowData,
          studentSubjectData,
        ] = await Promise.all([
          attendanceService.getStudentAttendance(params),
          attendanceService.getSubjectAttendance(params),
          attendanceService.getClassAttendance(selectedPeriod),
          attendanceService.getLowAttendanceStudents({
            ...params,
            threshold: 75,
          }),
          attendanceService.getStudentSubjectAttendance(params),
        ]);

        setStudents(studentData);
        setSubjects(subjectData);
        setClasses(classData);
        setLowAttendance(lowData);
        setStudentSubjects(studentSubjectData);
      } catch (err) {
        console.error("Failed to load attendance data:", err);
        setError("Unable to load attendance data. Please try again.");

        setStudents([]);
        setSubjects([]);
        setClasses([]);
        setLowAttendance([]);
        setStudentSubjects([]);
      } finally {
        setLoading(false);
      }
    };

    loadAttendance();
  }, [selectedPeriod, selectedClass]);

  const formatPercentage = (value: number | null) => {
    return value === null ? "N/A" : `${value.toFixed(2)}%`;
  };

  const getAttendanceClass = (value: number | null) => {
    if (value === null) return "attendance-neutral";
    if (value >= 85) return "attendance-good";
    if (value >= 75) return "attendance-warning";
    return "attendance-danger";
  };

  const totalSessions = students.reduce(
    (sum, item) => sum + item.total_sessions,
    0
  );

  const totalPresent = students.reduce(
    (sum, item) => sum + item.present_sessions,
    0
  );

  const totalAbsent = students.reduce(
    (sum, item) => sum + item.absent_sessions,
    0
  );

  const overallPercentage =
    totalSessions > 0
      ? (totalPresent / totalSessions) * 100
      : null;

  return (
    <div className="attendance-page">
      <div className="attendance-header">
        <div>
          <h1>Attendance Management</h1>
          <p>
            Monitor student attendance, identify attendance risks,
            and compare academic periods.
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="attendance-filters">
        <div className="attendance-filter">
          <label htmlFor="attendance-period">
            Academic Period
          </label>

          <select
            id="attendance-period"
            value={selectedPeriod}
            onChange={(e) =>
              setSelectedPeriod(
                e.target.value === "" ? "" : Number(e.target.value)
              )
            }
          >
            {periods.length === 0 && (
              <option value="">No periods available</option>
            )}

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

        <div className="attendance-filter">
          <label htmlFor="attendance-class">
            Class
          </label>

          <select
            id="attendance-class"
            value={selectedClass}
            onChange={(e) =>
              setSelectedClass(
                e.target.value === "" ? "" : Number(e.target.value)
              )
            }
          >
            <option value="">All Classes</option>

            {classes.map((item) => (
              <option key={item.class_id} value={item.class_id}>
                {item.grade} - Section {item.section}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="attendance-error">
          {error}
        </div>
      )}

      {loading && (
        <div className="attendance-loading">
          Loading attendance data...
        </div>
      )}

      {!loading && !error && selectedPeriod !== "" && (
        <>
          {/* Summary Cards */}
          <div className="attendance-summary-grid">
            <div className="attendance-summary-card">
              <span>Total Sessions</span>
              <h2>{totalSessions.toLocaleString()}</h2>
              <p>Recorded attendance sessions</p>
            </div>

            <div className="attendance-summary-card">
              <span>Present Sessions</span>
              <h2>{totalPresent.toLocaleString()}</h2>
              <p>Students marked present</p>
            </div>

            <div className="attendance-summary-card">
              <span>Absent Sessions</span>
              <h2>{totalAbsent.toLocaleString()}</h2>
              <p>Students marked absent</p>
            </div>

            <div className="attendance-summary-card">
              <span>Overall Attendance</span>
              <h2 className={getAttendanceClass(overallPercentage)}>
                {formatPercentage(overallPercentage)}
              </h2>
              <p>Based on recorded student sessions</p>
            </div>

            <div className="attendance-summary-card">
              <span>Low Attendance Students</span>
              <h2 className="attendance-danger">
                {lowAttendance.length}
              </h2>
              <p>Below 75% attendance</p>
            </div>
          </div>

          {/* Class Attendance */}
          <section className="attendance-section">
            <div className="attendance-section-header">
              <div>
                <h2>Class Attendance</h2>
                <p>Attendance summary by class</p>
              </div>
            </div>

            <div className="attendance-table-wrapper">
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Grade</th>
                    <th>Section</th>
                    <th>Students Recorded</th>
                    <th>Total Sessions</th>
                    <th>Present</th>
                    <th>Absent</th>
                    <th>Attendance</th>
                  </tr>
                </thead>

                <tbody>
                  {classes
                    .filter(
                      (item) =>
                        selectedClass === "" ||
                        item.class_id === selectedClass
                    )
                    .map((item) => (
                      <tr key={item.class_id}>
                        <td>{item.grade}</td>
                        <td>{item.section}</td>
                        <td>{item.students_recorded}</td>
                        <td>{item.total_sessions.toLocaleString()}</td>
                        <td>{item.present_sessions.toLocaleString()}</td>
                        <td>{item.absent_sessions.toLocaleString()}</td>
                        <td>
                          <span
                            className={`attendance-status ${getAttendanceClass(
                              item.attendance_percentage
                            )}`}
                          >
                            {formatPercentage(item.attendance_percentage)}
                          </span>
                        </td>
                      </tr>
                    ))}

                  {classes.length === 0 && (
                    <tr>
                      <td colSpan={7} className="attendance-empty">
                        No class attendance records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Student Attendance */}
          <section className="attendance-section">
            <div className="attendance-section-header">
              <div>
                <h2>Student Attendance</h2>
                <p>Individual student attendance records</p>
              </div>
            </div>

            <div className="attendance-table-wrapper">
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Admission No.</th>
                    <th>Student Name</th>
                    <th>Class</th>
                    <th>Total Sessions</th>
                    <th>Present</th>
                    <th>Absent</th>
                    <th>Attendance</th>
                  </tr>
                </thead>

                <tbody>
                  {students.map((item) => (
                    <tr key={item.student_id}>
                      <td>{item.admission_number}</td>
                      <td>
                        {item.first_name} {item.last_name}
                      </td>
                      <td>
                        {item.grade} - {item.section}
                      </td>
                      <td>{item.total_sessions}</td>
                      <td>{item.present_sessions}</td>
                      <td>{item.absent_sessions}</td>
                      <td>
                        <span
                          className={`attendance-status ${getAttendanceClass(
                            item.attendance_percentage
                          )}`}
                        >
                          {formatPercentage(item.attendance_percentage)}
                        </span>
                      </td>
                    </tr>
                  ))}

                  {students.length === 0 && (
                    <tr>
                      <td colSpan={7} className="attendance-empty">
                        No student attendance records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Low Attendance Alerts */}
          <section className="attendance-section">
            <div className="attendance-section-header">
              <div>
                <h2>Low Attendance Alerts</h2>
                <p>
                  Students with attendance below the 75% threshold
                </p>
              </div>

              <span className="attendance-alert-count">
                {lowAttendance.length} Students
              </span>
            </div>

            <div className="attendance-table-wrapper">
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Admission No.</th>
                    <th>Student Name</th>
                    <th>Class</th>
                    <th>Total Sessions</th>
                    <th>Present</th>
                    <th>Absent</th>
                    <th>Attendance</th>
                  </tr>
                </thead>

                <tbody>
                  {lowAttendance.map((item) => (
                    <tr key={item.student_id}>
                      <td>{item.admission_number}</td>
                      <td>
                        {item.first_name} {item.last_name}
                      </td>
                      <td>
                        {item.grade} - {item.section}
                      </td>
                      <td>{item.total_sessions}</td>
                      <td>{item.present_sessions}</td>
                      <td>{item.absent_sessions}</td>
                      <td>
                        <span className="attendance-status attendance-danger">
                          {formatPercentage(item.attendance_percentage)}
                        </span>
                      </td>
                    </tr>
                  ))}

                  {lowAttendance.length === 0 && (
                    <tr>
                      <td colSpan={7} className="attendance-empty">
                        No students below the attendance threshold.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Subject Attendance */}
          <section className="attendance-section">
            <div className="attendance-section-header">
              <div>
                <h2>Subject Attendance</h2>
                <p>Attendance summary by subject</p>
              </div>
            </div>

            <div className="attendance-table-wrapper">
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Subject Code</th>
                    <th>Subject</th>
                    <th>Students Recorded</th>
                    <th>Total Sessions</th>
                    <th>Present</th>
                    <th>Absent</th>
                    <th>Attendance</th>
                  </tr>
                </thead>

                <tbody>
                  {subjects.map((item) => (
                    <tr key={item.subject_id}>
                      <td>{item.subject_code}</td>
                      <td>{item.subject_name}</td>
                      <td>{item.students_recorded}</td>
                      <td>{item.total_sessions}</td>
                      <td>{item.present_sessions}</td>
                      <td>{item.absent_sessions}</td>
                      <td>
                        <span
                          className={`attendance-status ${getAttendanceClass(
                            item.attendance_percentage
                          )}`}
                        >
                          {formatPercentage(item.attendance_percentage)}
                        </span>
                      </td>
                    </tr>
                  ))}

                  {subjects.length === 0 && (
                    <tr>
                      <td colSpan={7} className="attendance-empty">
                        No subject attendance records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Student Subject Attendance */}
          <section className="attendance-section">
            <div className="attendance-section-header">
              <div>
                <h2>Student Subject Attendance</h2>
                <p>
                  Individual attendance breakdown for each subject
                </p>
              </div>
            </div>

            <div className="attendance-table-wrapper">
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Admission No.</th>
                    <th>Student Name</th>
                    <th>Class</th>
                    <th>Subject</th>
                    <th>Total Sessions</th>
                    <th>Present</th>
                    <th>Absent</th>
                    <th>Attendance</th>
                  </tr>
                </thead>

                <tbody>
                  {studentSubjects.map((item, index) => (
                    <tr
                      key={`${item.student_id}-${item.subject_id}-${index}`}
                    >
                      <td>{item.admission_number}</td>
                      <td>
                        {item.first_name} {item.last_name}
                      </td>
                      <td>
                        {item.grade} - {item.section}
                      </td>
                      <td>{item.subject_name}</td>
                      <td>{item.total_sessions}</td>
                      <td>{item.present_sessions}</td>
                      <td>{item.absent_sessions}</td>
                      <td>
                        <span
                          className={`attendance-status ${getAttendanceClass(
                            item.attendance_percentage
                          )}`}
                        >
                          {formatPercentage(item.attendance_percentage)}
                        </span>
                      </td>
                    </tr>
                  ))}

                  {studentSubjects.length === 0 && (
                    <tr>
                      <td colSpan={8} className="attendance-empty">
                        No student-subject attendance records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Academic Period Comparison */}
          <section className="attendance-section">
            <div className="attendance-section-header">
              <div>
                <h2>Academic Period Comparison</h2>
                <p>Compare attendance across academic periods</p>
              </div>
            </div>

            <div className="attendance-table-wrapper">
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Academic Period</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Students Recorded</th>
                    <th>Total Sessions</th>
                    <th>Present</th>
                    <th>Absent</th>
                    <th>Attendance</th>
                  </tr>
                </thead>

                <tbody>
                  {periods.map((item) => (
                    <tr key={item.academic_period_id}>
                      <td>{item.academic_period_name}</td>
                      <td>{item.start_date}</td>
                      <td>{item.end_date}</td>
                      <td>{item.students_recorded}</td>
                      <td>{item.total_sessions}</td>
                      <td>{item.present_sessions}</td>
                      <td>{item.absent_sessions}</td>
                      <td>
                        <span
                          className={`attendance-status ${getAttendanceClass(
                            item.attendance_percentage
                          )}`}
                        >
                          {formatPercentage(item.attendance_percentage)}
                        </span>
                      </td>
                    </tr>
                  ))}

                  {periods.length === 0 && (
                    <tr>
                      <td colSpan={8} className="attendance-empty">
                        No academic period comparison data available.
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
};

export default Attendance;
