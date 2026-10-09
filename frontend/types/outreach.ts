export type OutreachStatus =
  | "PREPARED"
  | "PENDING_APPROVAL"
  | "APPROVED"
  | "SENT"
  | "FAILED"
  | "REPLIED"
  | "OPTED_OUT";

export interface Outreach {
  id: string;
  lead_id: string;
  campaign_id: string | null;
  owner_id: string;
  channel: string;
  subject: string | null;
  body: string;
  status: OutreachStatus;
  error: string | null;
  approved_at: string | null;
  sent_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface OutreachPrepareRequest {
  lead_id: string;
  campaign_id?: string | null;
  channel?: "email";
}
