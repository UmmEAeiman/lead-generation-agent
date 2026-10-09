import Link from "next/link";

import { serverApiRequest } from "@/lib/api/server";
import { formatPercent } from "@/lib/format";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Table, Td, Th } from "@/components/ui/Table";
import { AGENT_TYPE_LABELS, LEAD_STATUS_META, RUN_STATUS_META } from "@/lib/statusMeta";
import type { Page } from "@/types/api";
import type { AgentRun } from "@/types/agent";
import type { LeadStatus } from "@/types/lead";

export async function RecentLeads() {
  let leads: Array<{
    id: string;
    company_name: string;
    status: LeadStatus;
    lead_score: number | null;
  }>;
  try {
    const leadPage = await serverApiRequest<{
      items: Array<{
        id: string;
        company_name: string;
        status: LeadStatus;
        lead_score: number | null;
      }>;
      total: number;
    }>("/api/v1/leads?page=1&page_size=5");
    leads = leadPage.items;
  } catch {
    leads = [];
  }

  return (
    <Card
      title="Recent leads"
      description="The latest leads added to your workspace"
      actions={
        <Link href="/dashboard/leads" className="text-sm font-medium text-primary hover:underline">
          View all
        </Link>
      }
    >
      {leads.length === 0 ? (
        <EmptyState
          title="No leads yet"
          description="Add a lead manually or run the discovery agent."
        />
      ) : (
        <Table>
          <thead>
            <tr>
              <Th>Company</Th>
              <Th>Status</Th>
              <Th className="text-right">Score</Th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id}>
                <Td>
                  <a
                    href={`/dashboard/leads/${lead.id}`}
                    className="font-medium text-foreground hover:text-primary hover:underline"
                  >
                    {lead.company_name}
                  </a>
                </Td>
                <Td>
                  {(() => {
                    const meta = LEAD_STATUS_META[lead.status];
                    return <Badge tone={meta.tone}>{meta.label}</Badge>;
                  })()}
                </Td>
                <Td className="text-right">{lead.lead_score ?? "—"}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Card>
  );
}

export async function AgentActivity() {
  let runs: AgentRun[] = [];
  try {
    const page = await serverApiRequest<Page<AgentRun>>(
      "/api/v1/agents/runs?page=1&page_size=5",
    );
    runs = page.items;
  } catch {
    runs = [];
  }

  return (
    <Card
      title="Agent activity"
      description="Recent background runs"
      actions={
        <Link href="/dashboard/agents" className="text-sm font-medium text-primary hover:underline">
          Open agents
        </Link>
      }
    >
      {runs.length === 0 ? (
        <EmptyState
          title="No agent runs yet"
          description="Queue discovery, qualification, or the full pipeline from the Agents page."
        />
      ) : (
        <ul className="flex flex-col divide-y divide-border">
          {runs.map((run) => {
            const meta = RUN_STATUS_META[run.status];
            return (
              <li key={run.run_id} className="flex items-center justify-between gap-3 py-3">
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {AGENT_TYPE_LABELS[run.agent_type]}
                  </p>
                  <p className="text-xs text-muted">{run.run_id}</p>
                </div>
                <Badge tone={meta.tone}>{meta.label}</Badge>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}

export async function AgentSuccessRate() {
  let successRate: number | null = null;
  let total = 0;
  let failed = 0;
  try {
    const data = await serverApiRequest<{
      agent_success_rate: number | null;
      agent_runs_total: number;
      agent_runs_failed: number;
    }>("/api/v1/analytics/overview");
    successRate = data.agent_success_rate;
    total = data.agent_runs_total;
    failed = data.agent_runs_failed;
  } catch {
    successRate = null;
  }

  return (
    <Card title="Agent reliability" description="Successful vs. failed runs">
      <p className="text-3xl font-semibold text-foreground">
        {successRate === null ? "—" : formatPercent(successRate)}
      </p>
      <p className="mt-1 text-sm text-muted">
        {total} run{total === 1 ? "" : "s"} total · {failed} failed
      </p>
    </Card>
  );
}
