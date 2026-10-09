import { formatPercent, formatRelative } from "@/lib/format";
import { serverApiRequest } from "@/lib/api/server";
import { LEAD_STATUSES, agentLabel } from "@/lib/statusMeta";
import type { AnalyticsOverview } from "@/types/analytics";
import type { Page } from "@/types/api";
import type { AgentRun } from "@/types/agent";
import type { User } from "@/types/auth";
import type { Lead, LeadStatus } from "@/types/lead";
import type { Outreach } from "@/types/outreach";

export interface StatCardData {
  label: string;
  value: number;
  sub: string;
}

export interface DonutBucket {
  label: string;
  value: number;
  color: string;
}

export interface ActivityItem {
  id: string;
  title: string;
  source: string;
  at: string;
}

export interface AgentStatusItem {
  id: string;
  label: string;
  statusText: string;
  tone: "muted" | "success" | "danger";
}

export interface RecentLeadRow {
  id: string;
  name: string;
  company: string;
  email: string | null;
  score: number | null;
  status: LeadStatus;
  createdAt: string;
}

export interface ChartLead {
  created_at: string;
  status: LeadStatus;
}

export interface DashboardData {
  user: User;
  greeting: string;
  greetingName: string;
  stats: StatCardData[];
  donutTotal: number;
  buckets: DonutBucket[];
  chartLeads: ChartLead[];
  chartTruncated: boolean;
  agentItems: AgentStatusItem[];
  anyRunning: boolean;
  activity: ActivityItem[];
  recentLeads: RecentLeadRow[];
  clock: { date: string; time: string };
}

const SCAN_PAGE_SIZE = 100;
const SCAN_MAX_LEADS = 1000;

const BUCKETS: Array<{ label: string; color: string; statuses: LeadStatus[] }> = [
  { label: "New", color: "#1e67fd", statuses: ["NEW"] },
  { label: "Enriching", color: "#9aa7bd", statuses: ["ENRICHING"] },
  { label: "Contacted", color: "#7636f1", statuses: ["CONTACTED"] },
  { label: "Replied", color: "#60a5fa", statuses: ["REPLIED"] },
  { label: "Qualified", color: "#35d49d", statuses: ["QUALIFIED"] },
  { label: "Interested", color: "#ff971b", statuses: ["INTERESTED"] },
  { label: "Meeting booked", color: "#8c5ae9", statuses: ["MEETING_BOOKED"] },
  { label: "Converted", color: "#08b4c3", statuses: ["CONVERTED"] },
  { label: "Lost", color: "#f64e62", statuses: ["UNQUALIFIED", "REJECTED"] },
  { label: "Do not contact", color: "#e5485c", statuses: ["DO_NOT_CONTACT"] },
];

async function safeRequest<T>(path: string, fallback: T): Promise<T> {
  try {
    return await serverApiRequest<T>(path);
  } catch {
    return fallback;
  }
}

async function fetchLeadScan(total: number): Promise<Lead[]> {
  const pageCount = Math.max(1, Math.ceil(Math.min(total, SCAN_MAX_LEADS) / SCAN_PAGE_SIZE));
  const paths = Array.from(
    { length: pageCount },
    (_, index) =>
      `/api/v1/leads?page=${index + 1}&page_size=${SCAN_PAGE_SIZE}&sort=created_at&order=desc`,
  );
  const pages = await Promise.all(
    paths.map((path) =>
      safeRequest<Page<Lead>>(path, { items: [], total: 0, page: 1, page_size: SCAN_PAGE_SIZE }),
    ),
  );
  return pages.flatMap((page) => page.items);
}

function greetingForHour(hour: number): string {
  if (hour >= 5 && hour < 12) return "Good morning";
  if (hour >= 12 && hour < 17) return "Good afternoon";
  return "Good evening";
}

function leadDisplay(lead: Lead): string {
  return lead.contact_name || lead.company_name;
}

function runStatusItem(run: AgentRun): AgentStatusItem {
  const time = run.completed_at || run.started_at;
  switch (run.status) {
    case "completed":
      return {
        id: run.run_id,
        label: agentLabel(run.agent_type),
        statusText: `Completed · ${formatRelative(time)}`,
        tone: "muted",
      };
    case "running":
      return {
        id: run.run_id,
        label: agentLabel(run.agent_type),
        statusText: "Running",
        tone: "success",
      };
    case "failed":
      return {
        id: run.run_id,
        label: agentLabel(run.agent_type),
        statusText: `Failed · ${formatRelative(time)}`,
        tone: "danger",
      };
    case "cancelled":
      return {
        id: run.run_id,
        label: agentLabel(run.agent_type),
        statusText: `Cancelled · ${formatRelative(time)}`,
        tone: "muted",
      };
    default:
      return {
        id: run.run_id,
        label: agentLabel(run.agent_type),
        statusText: "Pending",
        tone: "muted",
      };
  }
}

function buildActivity(
  leads: Lead[],
  sent: Outreach[],
  runs: AgentRun[],
): ActivityItem[] {
  const nameById = new Map(leads.map((lead) => [lead.id, leadDisplay(lead)]));
  const items: ActivityItem[] = [
    ...leads.slice(0, 4).map((lead) => ({
      id: `lead-${lead.id}`,
      title: `New lead added: ${leadDisplay(lead)}`,
      source: lead.source || "Manual entry",
      at: lead.created_at,
    })),
    ...sent.map((outreach) => ({
      id: `outreach-${outreach.id}`,
      title: nameById.has(outreach.lead_id)
        ? `Outreach sent to ${nameById.get(outreach.lead_id)}`
        : outreach.subject
          ? `Outreach sent: ${outreach.subject}`
          : `Outreach sent via ${outreach.channel}`,
      source: outreach.channel,
      at: outreach.sent_at || outreach.created_at,
    })),
    ...runs
      .filter((run) => run.status === "completed" || run.status === "failed" || run.status === "running")
      .map((run) => ({
        id: `run-${run.run_id}`,
        title: `${agentLabel(run.agent_type)} run ${
          run.status === "running" ? "started" : run.status
        }`,
        source: "Agent run",
        at: run.completed_at || run.started_at || "",
      })),
  ];
  return items
    .filter((item) => item.at && !Number.isNaN(new Date(item.at).getTime()))
    .sort((a, b) => new Date(b.at).getTime() - new Date(a.at).getTime())
    .slice(0, 6);
}

export async function getDashboardData(): Promise<DashboardData> {
  const [user, overview, runsPage, sentPage, countPages] = await Promise.all([
    serverApiRequest<User>("/api/v1/users/me"),
    serverApiRequest<AnalyticsOverview>("/api/v1/analytics/overview"),
    safeRequest<Page<AgentRun>>("/api/v1/agents/runs?page=1&page_size=6", {
      items: [],
      total: 0,
      page: 1,
      page_size: 6,
    }),
    safeRequest<Page<Outreach>>("/api/v1/outreach?status=SENT&page=1&page_size=5", {
      items: [],
      total: 0,
      page: 1,
      page_size: 5,
    }),
    Promise.all(
      LEAD_STATUSES.map((statusValue) =>
        safeRequest<{ total: number }>(
          `/api/v1/leads?status=${statusValue}&page=1&page_size=1`,
          { total: 0 },
        ),
      ),
    ),
  ]);

  const scan = await fetchLeadScan(overview.total_leads);

  const countByStatus = new Map<LeadStatus, number>(
    LEAD_STATUSES.map((statusValue, index) => [statusValue, countPages[index].total]),
  );
  const buckets = BUCKETS.map((bucket) => ({
    label: bucket.label,
    color: bucket.color,
    value: bucket.statuses.reduce(
      (sum, statusValue) => sum + (countByStatus.get(statusValue) ?? 0),
      0,
    ),
  })).filter((bucket) => bucket.value > 0);

  const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
  const addedThisWeek = scan.filter(
    (lead) => new Date(lead.created_at).getTime() >= weekAgo,
  ).length;

  const now = new Date();
  const greetingName = (user.full_name || user.email.split("@")[0]).split(/\s+/)[0];

  return {
    user,
    greeting: greetingForHour(now.getUTCHours()),
    greetingName,
    stats: [
      {
        label: "Total Leads",
        value: overview.total_leads,
        sub: `${addedThisWeek} added this week`,
      },
      {
        label: "Qualified Leads",
        value: overview.qualified_leads,
        sub: `${formatPercent(overview.qualification_rate)} qualification rate`,
      },
      {
        label: "Outreach Sent",
        value: sentPage.total,
        sub: `${overview.replies} replies received`,
      },
      {
        label: "Meetings Booked",
        value: overview.meetings,
        sub: `${overview.conversions} conversions`,
      },
    ],
    donutTotal: overview.total_leads,
    buckets,
    chartLeads: scan.map((lead) => ({ created_at: lead.created_at, status: lead.status })),
    chartTruncated: overview.total_leads > SCAN_MAX_LEADS,
    agentItems: runsPage.items.map(runStatusItem),
    anyRunning: runsPage.items.some((run) => run.status === "running"),
    activity: buildActivity(scan, sentPage.items, runsPage.items),
    recentLeads: scan.slice(0, 5).map((lead) => ({
      id: lead.id,
      name: leadDisplay(lead),
      company: lead.company_name,
      email: lead.email,
      score: lead.lead_score,
      status: lead.status,
      createdAt: lead.created_at,
    })),
    clock: {
      date: now.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        timeZone: "UTC",
      }),
      time: `${now.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        timeZone: "UTC",
      })} (UTC)`,
    },
  };
}
