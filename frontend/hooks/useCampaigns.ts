"use client";

import { useAsync } from "@/hooks/useAsync";
import { listCampaigns } from "@/lib/api/campaigns";
import type { Page } from "@/types/api";
import type { Campaign } from "@/types/campaign";

export function useCampaigns() {
  return useAsync<Page<Campaign>>(() => listCampaigns(1, 100), []);
}
