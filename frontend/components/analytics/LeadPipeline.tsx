import { serverApiRequest } from "@/lib/api/server";
import { formatPercent } from "@/lib/format";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import type { AnalyticsOverview } from "@/types/analytics";

function StageBar({ label, value, total }: { label: string; value: number; total: number }) {
  const width = total > 0 ? Math.max(2, Math.round((value / total) * 100)) : 0;
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="text-foreground">{label}</span>
        <span className="text-muted">
          {value} · {total > 0 ? formatPercent((value / total) * 100) : "0%"}
        </span>
      </div>
      <div
        role="img"
        aria-label={`${label}: ${value} of ${total}`}
        className="h-2.5 w-full overflow-hidden rounded-full bg-muted-background"
      >
        <div className="h-full rounded-full bg-primary" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

export async function LeadPipeline() {
  let data: AnalyticsOverview;
  try {
    data = (await serverApiRequest<AnalyticsOverview>(
      "/api/v1/analytics/overview",
    )) as AnalyticsOverview;
  } catch {
    data = {
      total_leads: 0,
      qualified_leads: 0,
      hot_leads: 0,
      contacted_leads: 0,
      replies: 0,
      positive_replies: 0,
      meetings: 0,
      conversions: 0,
      do_not_contact: 0,
      qualification_rate: 0,
      reply_rate: 0,
      conversion_rate: 0,
      campaign_performance: [],
      agent_success_rate: null,
      agent_runs_total: 0,
      agent_runs_failed: 0,
    };
  }

  if (data.total_leads === 0) {
    return (
      <Card title="Lead pipeline">
        <EmptyState
          title="No leads yet"
          description="Run the discovery agent to build your pipeline."
        />
      </Card>
    );
  }

  return (
    <Card title="Lead pipeline" description="From total leads to closed deals">
      <div className="flex flex-col gap-4">
        <StageBar label="Total leads" value={data.total_leads} total={data.total_leads} />
        <StageBar label="Qualified" value={data.qualified_leads} total={data.total_leads} />
        <StageBar label="Contacted" value={data.contacted_leads} total={data.total_leads} />
        <StageBar label="Replies" value={data.replies} total={data.total_leads} />
        <StageBar label="Meetings" value={data.meetings} total={data.total_leads} />
        <StageBar label="Conversions" value={data.conversions} total={data.total_leads} />
      </div>
    </Card>
  );
}
