
import api from "./api";
import type { DashboardOverview } from "../types/dashboard";

export const dashboardService = {
  async getOverview(
    academicPeriodId?: number
  ): Promise<DashboardOverview> {
    const response = await api.get<DashboardOverview>(
      "/dashboard/overview",
      {
        params: academicPeriodId
          ? { academic_period_id: academicPeriodId }
          : undefined,
      }
    );

    return response.data;
  },
};

export default dashboardService;
