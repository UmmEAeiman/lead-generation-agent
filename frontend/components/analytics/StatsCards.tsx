import { ApiRequestError } from "@/lib/api/client";
import { serverApiRequest } from "@/lib/api/server";
import { formatPercent } from "@/lib/format";
import { ErrorState } from "@/components/ui/ErrorState";
import type { AnalyticsOverview } from "@/types/analytics";

function StatTile({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-foreground">{value}</p>
      {hint ? <p className="mt-0.5 text-xs text-muted">{hint}</p> : null}
    </div>
  );
}

function errorMessage(error: unknown): string {
  if (error instanceof ApiRequestError) return error.message;
  return "Could not load overview metrics.";
}

export async function StatsCards() {
  let data: AnalyticsOverview | null = null;
  let failure: string | null = null;
  try {
    data = await serverApiRequest<AnalyticsOverview>("/api/v1/analytics/overview");
  } catch (error) {
    failure = errorMessage(error);
  }

  if (failure || !data) {
    return <ErrorState message={failure ?? "Could not load overview metrics."} />;
  }

  const overview: AnalyticsOverview = data;

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      <StatTile label="Total leads" value={overview.total_leads} />
      <StatTile
        label="Qualified"
        value={overview.qualified_leads}
        hint={`${formatPercent(overview.qualification_rate)} qualification rate`}
      />
      <StatTile label="Hot leads" value={overview.hot_leads} />
      <StatTile label="Contacted" value={overview.contacted_leads} />
      <StatTile
        label="Replies"
        value={overview.replies}
        hint={`${formatPercent(overview.reply_rate)} reply rate`}
      />
      <StatTile label="Positive replies" value={overview.positive_replies} />
      <StatTile label="Meetings" value={overview.meetings} />
      <StatTile
        label="Conversions"
        value={overview.conversions}
        hint={`${formatPercent(overview.conversion_rate)} conversion rate`}
      />
    </div>
  );
}
