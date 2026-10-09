import type { BadgeTone } from "@/components/ui/Badge";
import type { AgentRunStatus, AgentType } from "@/types/agent";
import type { CampaignStatus } from "@/types/campaign";
import type { FollowupState, LeadStatus, Qualification } from "@/types/lead";
import type { OutreachStatus } from "@/types/outreach";

interface StatusMeta {
  label: string;
  tone: BadgeTone;
}

export const LEAD_STATUS_META: Record<LeadStatus, StatusMeta> = {
  NEW: { label: "New", tone: "primary" },
  ENRICHING: { label: "Enriching", tone: "neutral" },
  QUALIFIED: { label: "Qualified", tone: "success" },
  UNQUALIFIED: { label: "Unqualified", tone: "danger" },
  CONTACTED: { label: "Contacted", tone: "violet" },
  REPLIED: { label: "Replied", tone: "violet" },
  INTERESTED: { label: "Interested", tone: "warning" },
  MEETING_BOOKED: { label: "Meeting booked", tone: "success" },
  CONVERTED: { label: "Converted", tone: "cyan" },
  REJECTED: { label: "Rejected", tone: "danger" },
  DO_NOT_CONTACT: { label: "Do not contact", tone: "danger" },
};

export const LEAD_STATUSES = Object.keys(LEAD_STATUS_META) as LeadStatus[];

export const CAMPAIGN_STATUS_META: Record<CampaignStatus, StatusMeta> = {
  DRAFT: { label: "Draft", tone: "neutral" },
  ACTIVE: { label: "Active", tone: "success" },
  PAUSED: { label: "Paused", tone: "warning" },
  COMPLETED: { label: "Completed", tone: "info" },
};

export const OUTREACH_STATUS_META: Record<OutreachStatus, StatusMeta> = {
  PREPARED: { label: "Prepared", tone: "neutral" },
  PENDING_APPROVAL: { label: "Pending approval", tone: "warning" },
  APPROVED: { label: "Approved", tone: "primary" },
  SENT: { label: "Sent", tone: "success" },
  FAILED: { label: "Failed", tone: "danger" },
  REPLIED: { label: "Replied", tone: "success" },
  OPTED_OUT: { label: "Opted out", tone: "danger" },
};

export const RUN_STATUS_META: Record<AgentRunStatus, StatusMeta> = {
  queued: { label: "Queued", tone: "neutral" },
  running: { label: "Running", tone: "success" },
  completed: { label: "Completed", tone: "neutral" },
  failed: { label: "Failed", tone: "danger" },
  cancelled: { label: "Cancelled", tone: "warning" },
};

export const AGENT_TYPE_LABELS: Record<AgentType, string> = {
  discovery: "Discovery",
  enrichment: "Enrichment",
  research: "Research",
  qualification: "Qualification",
  personalization: "Personalization",
  followup: "Follow-up",
  pipeline: "Full Pipeline",
};

export function agentLabel(agentType: AgentType): string {
  return `${AGENT_TYPE_LABELS[agentType]} Agent`;
}

export const QUALIFICATION_META: Record<Qualification, StatusMeta> = {
  high: { label: "High", tone: "success" },
  medium: { label: "Medium", tone: "warning" },
  low: { label: "Low", tone: "danger" },
  unknown: { label: "Not scored", tone: "neutral" },
};

export const FOLLOWUP_STATE_LABELS: Record<FollowupState, string> = {
  NO_RESPONSE: "No response",
  INTERESTED: "Interested",
  NOT_INTERESTED: "Not interested",
  NEEDS_INFO: "Needs info",
  MEETING_REQUESTED: "Meeting requested",
  MEETING_BOOKED: "Meeting booked",
  DO_NOT_CONTACT: "Do not contact",
};
