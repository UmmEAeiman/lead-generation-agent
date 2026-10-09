import { apiRequest } from "@/lib/api/client";
import type { Page } from "@/types/api";
import type { Campaign, CampaignCreate, CampaignUpdate } from "@/types/campaign";

export function listCampaigns(page = 1, pageSize = 50): Promise<Page<Campaign>> {
  return apiRequest<Page<Campaign>>(
    `/api/v1/campaigns?page=${page}&page_size=${pageSize}`,
  );
}

export function createCampaign(data: CampaignCreate): Promise<Campaign> {
  return apiRequest<Campaign>("/api/v1/campaigns", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateCampaign(
  campaignId: string,
  data: CampaignUpdate,
): Promise<Campaign> {
  return apiRequest<Campaign>(`/api/v1/campaigns/${campaignId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}
