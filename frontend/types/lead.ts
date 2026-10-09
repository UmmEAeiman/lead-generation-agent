export type LeadStatus =
  | "NEW"
  | "ENRICHING"
  | "QUALIFIED"
  | "UNQUALIFIED"
  | "CONTACTED"
  | "REPLIED"
  | "INTERESTED"
  | "MEETING_BOOKED"
  | "CONVERTED"
  | "REJECTED"
  | "DO_NOT_CONTACT";

export type Qualification = "low" | "medium" | "high" | "unknown";

export type FollowupState =
  | "NO_RESPONSE"
  | "INTERESTED"
  | "NOT_INTERESTED"
  | "NEEDS_INFO"
  | "MEETING_REQUESTED"
  | "MEETING_BOOKED"
  | "DO_NOT_CONTACT";

export type DataConfidence = "verified" | "unverified" | "unknown";

export interface Lead {
  id: string;
  owner_id: string;
  company_name: string;
  website: string | null;
  industry: string | null;
  location: string | null;
  company_size: string | null;
  contact_name: string | null;
  contact_role: string | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  source: string | null;
  source_url: string | null;
  description: string | null;
  lead_score: number | null;
  qualification: Qualification;
  qualification_reasons: string[];
  status: LeadStatus;
  followup_state: FollowupState | null;
  research_summary: string | null;
  pain_points: string[];
  personalized_message: string | null;
  field_confidence: Record<string, DataConfidence | string>;
  created_at: string;
  updated_at: string;
}

export interface LeadCreate {
  company_name: string;
  website?: string | null;
  industry?: string | null;
  location?: string | null;
  company_size?: string | null;
  contact_name?: string | null;
  contact_role?: string | null;
  email?: string | null;
  phone?: string | null;
  linkedin_url?: string | null;
  source?: string | null;
  source_url?: string | null;
  description?: string | null;
}

export interface LeadUpdate extends Partial<LeadCreate> {
  status?: LeadStatus;
  followup_state?: FollowupState;
}

export interface LeadFilters {
  q?: string;
  status?: LeadStatus | "";
  industry?: string;
  location?: string;
  score_min?: number;
  score_max?: number;
  sort?: string;
  order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}
