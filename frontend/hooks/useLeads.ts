"use client";

import { useAsync } from "@/hooks/useAsync";
import { getLead, listLeads } from "@/lib/api/leads";
import type { Page } from "@/types/api";
import type { Lead, LeadFilters } from "@/types/lead";

export function useLeads(filters: LeadFilters): AsyncStatePage<Lead> {
  return useAsync<Page<Lead>>(() => listLeads(filters), [
    filters.q,
    filters.status,
    filters.industry,
    filters.location,
    filters.score_min,
    filters.score_max,
    filters.run_id,
    filters.campaign_id,
    filters.ids?.join(",") ?? "",
    filters.sort,
    filters.order,
    filters.page,
    filters.page_size,
  ]);
}

export type AsyncStatePage<T> = {
  data: Page<T> | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
};

export function useLead(leadId: string) {
  return useAsync<Lead>(() => getLead(leadId), [leadId]);
}
