"use client";

import { useAsync } from "@/hooks/useAsync";
import { getOverview } from "@/lib/api/analytics";
import type { AnalyticsOverview } from "@/types/analytics";

export function useAnalytics() {
  return useAsync<AnalyticsOverview>(() => getOverview(), []);
}
