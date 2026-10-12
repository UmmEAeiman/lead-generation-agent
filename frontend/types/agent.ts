export type AgentType =
  | "discovery"
  | "enrichment"
  | "research"
  | "qualification"
  | "personalization"
  | "followup"
  | "pipeline";

export type AgentRunStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export interface AgentRun {
  run_id: string;
  agent_type: AgentType;
  user_id: string | null;
  campaign_id: string | null;
  status: AgentRunStatus;
  progress: number | null;
  input_summary: Record<string, unknown>;
  output_summary: Record<string, unknown>;
  error: string | null;
  tokens_used: number | null;
  duration: number | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface QueuedRun {
  run_id: string;
  status: AgentRunStatus;
}

export interface AgentRunRequest {
  lead_ids?: string[];
  campaign_id?: string | null;
  icp?: IcpInput | null;
  limit?: number | null;
  prepare_outreach?: boolean;
}

export interface IcpInput {
  industry?: string;
  location?: string;
  company_size?: string;
  keywords?: string[];
}
