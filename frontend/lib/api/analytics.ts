import { apiRequest } from "@/lib/api/client";
import type { AnalyticsOverview } from "@/types/analytics";

export function getOverview(): Promise<AnalyticsOverview> {
  return apiRequest<AnalyticsOverview>("/api/v1/analytics/overview");
}
