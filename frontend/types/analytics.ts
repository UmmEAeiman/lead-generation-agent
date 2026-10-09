export interface CampaignPerformanceRow {
  campaign_id: string;
  name: string;
  total_leads: number;
  qualified: number;
  contacted: number;
  replies: number;
  conversions: number;
}

export interface AnalyticsOverview {
  total_leads: number;
  qualified_leads: number;
  hot_leads: number;
  contacted_leads: number;
  replies: number;
  positive_replies: number;
  meetings: number;
  conversions: number;
  do_not_contact: number;
  qualification_rate: number;
  reply_rate: number;
  conversion_rate: number;
  campaign_performance: CampaignPerformanceRow[];
  agent_success_rate: number | null;
  agent_runs_total: number;
  agent_runs_failed: number;
}
