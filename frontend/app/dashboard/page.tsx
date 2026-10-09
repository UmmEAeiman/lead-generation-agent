import { Suspense } from "react";

import { DashboardOverview } from "@/components/dashboard/DashboardOverview";
import { Skeleton } from "@/components/ui/Skeleton";

function OverviewFallback() {
  return (
    <div className="flex flex-col gap-6">
      <Skeleton className="h-28 w-full" />
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <Skeleton key={index} className="h-24" />
        ))}
      </div>
      <Skeleton className="h-80 w-full" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<OverviewFallback />}>
      <DashboardOverview />
    </Suspense>
  );
}
