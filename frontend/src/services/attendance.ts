
import api from "./api";

import type {
  StudentAttendance,
  SubjectAttendance,
  ClassAttendance,
  LowAttendanceStudent,
  StudentSubjectAttendance,
  AcademicPeriodAttendanceComparison,
} from "../types/attendance";

const attendanceService = {
  // 1. Fetch student attendance.
  async getStudentAttendance(params: {
    academic_period_id: number;
    class_id?: number;
    student_id?: number;
  }): Promise<StudentAttendance[]> {
    const response = await api.get<StudentAttendance[]>(
      "/analytics/attendance/students",
      { params }
    );

    return response.data;
  },

  // 2. Fetch subject-wise attendance.
  async getSubjectAttendance(params: {
    academic_period_id: number;
    class_id?: number;
  }): Promise<SubjectAttendance[]> {
    const response = await api.get<SubjectAttendance[]>(
      "/analytics/attendance/subjects",
      { params }
    );

    return response.data;
  },

  // 3. Fetch class-wise attendance.
  async getClassAttendance(
    academicPeriodId: number
  ): Promise<ClassAttendance[]> {
    const response = await api.get<ClassAttendance[]>(
      "/analytics/attendance/classes",
      {
        params: {
          academic_period_id: academicPeriodId,
        },
      }
    );

    return response.data;
  },

  // 4. Fetch students below the attendance threshold.
  async getLowAttendanceStudents(params: {
    academic_period_id: number;
    threshold?: number;
    class_id?: number;
  }): Promise<LowAttendanceStudent[]> {
    const response = await api.get<LowAttendanceStudent[]>(
      "/analytics/attendance/low-attendance",
      { params }
    );

    return response.data;
  },

  // 5. Fetch student-wise subject attendance.
  async getStudentSubjectAttendance(params: {
    academic_period_id: number;
    class_id?: number;
    student_id?: number;
  }): Promise<StudentSubjectAttendance[]> {
    const response = await api.get<StudentSubjectAttendance[]>(
      "/analytics/attendance/student-subjects",
      { params }
    );

    return response.data;
  },

  // 6. Compare attendance across academic periods.
  async getAcademicPeriodComparison():
    Promise<AcademicPeriodAttendanceComparison[]> {
    const response = await api.get<AcademicPeriodAttendanceComparison[]>(
      "/analytics/attendance/period-comparison"
    );

    return response.data;
  },
};

export default attendanceService;
