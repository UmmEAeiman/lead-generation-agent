import { Suspense } from "react";

import { CampaignPerformance } from "@/components/analytics/CampaignPerformance";
import { LeadPipeline } from "@/components/analytics/LeadPipeline";
import { StatsCards } from "@/components/analytics/StatsCards";
import { AgentSuccessRate } from "@/components/dashboard/DashboardSections";
import { Skeleton } from "@/components/ui/Skeleton";

export const metadata = { title: "Analytics · AI Lead Generation Agent" };

function SectionFallback() {
  return <Skeleton className="h-64 w-full" />;
}

export default function AnalyticsPage() {
  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-xl font-semibold text-foreground">Analytics</h1>
        <p className="mt-1 text-sm text-muted">
          Conversion metrics computed from your persisted data — never estimates.
        </p>
      </header>

      <Suspense
        fallback={
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {Array.from({ length: 8 }, (_, index) => (
              <Skeleton key={index} className="h-24" />
            ))}
          </div>
        }
      >
        <StatsCards />
      </Suspense>

      <div className="grid gap-6 lg:grid-cols-3">
        <Suspense fallback={<SectionFallback />}>
          <LeadPipeline />
        </Suspense>
        <div className="lg:col-span-2">
          <Suspense fallback={<SectionFallback />}>
            <AgentSuccessRate />
          </Suspense>
        </div>
      </div>

      <Suspense fallback={<SectionFallback />}>
        <CampaignPerformance />
      </Suspense>
    </div>
  );
}
