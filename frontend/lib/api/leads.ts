import { apiRequest } from "@/lib/api/client";
import type { Page } from "@/types/api";
import type { Lead, LeadCreate, LeadFilters, LeadUpdate } from "@/types/lead";

function queryString(filters: LeadFilters): string {
  const params = new URLSearchParams();
  const entries: Array<[string, string | number | undefined]> = [
    ["q", filters.q],
    ["status", filters.status || undefined],
    ["industry", filters.industry],
    ["location", filters.location],
    ["score_min", filters.score_min],
    ["score_max", filters.score_max],
    ["sort", filters.sort],
    ["order", filters.order],
    ["page", filters.page],
    ["page_size", filters.page_size],
  ];
  for (const [key, value] of entries) {
    if (value !== undefined && value !== "") params.set(key, String(value));
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function listLeads(filters: LeadFilters = {}): Promise<Page<Lead>> {
  return apiRequest<Page<Lead>>(`/api/v1/leads${queryString(filters)}`);
}

export function getLead(leadId: string): Promise<Lead> {
  return apiRequest<Lead>(`/api/v1/leads/${leadId}`);
}

export function createLead(data: LeadCreate): Promise<Lead> {
  return apiRequest<Lead>("/api/v1/leads", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateLead(leadId: string, data: LeadUpdate): Promise<Lead> {
  return apiRequest<Lead>(`/api/v1/leads/${leadId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteLead(leadId: string): Promise<void> {
  return apiRequest<void>(`/api/v1/leads/${leadId}`, { method: "DELETE" });
}

export function optOutLead(leadId: string): Promise<void> {
  return apiRequest<void>(`/api/v1/leads/${leadId}/opt-out`, { method: "POST" });
}
