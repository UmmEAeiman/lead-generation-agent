export type CampaignStatus = "DRAFT" | "ACTIVE" | "PAUSED" | "COMPLETED";

export interface Campaign {
  id: string;
  owner_id: string;
  name: string;
  description: string | null;
  status: CampaignStatus;
  target_industry: string | null;
  target_location: string | null;
  target_company_size: string | null;
  keywords: string[];
  created_at: string;
  updated_at: string;
}

export interface CampaignCreate {
  name: string;
  description?: string | null;
  target_industry?: string | null;
  target_location?: string | null;
  target_company_size?: string | null;
  keywords?: string[];
}

export interface CampaignUpdate extends Partial<CampaignCreate> {
  status?: CampaignStatus;
}
