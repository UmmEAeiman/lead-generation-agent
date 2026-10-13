import { apiRequest } from "@/lib/api/client";
import type { Page } from "@/types/api";
import type { Outreach, OutreachPrepareRequest } from "@/types/outreach";

export function listOutreach(
  options: {
    status?: string;
    leadId?: string;
    page?: number;
    pageSize?: number;
    run_id?: string;
    campaign_id?: string;
  } = {},
): Promise<Page<Outreach>> {
  const params = new URLSearchParams();
  if (options.status) params.set("status", options.status);
  if (options.leadId) params.set("lead_id", options.leadId);
  if (options.run_id) params.set("run_id", options.run_id);
  if (options.campaign_id) params.set("campaign_id", options.campaign_id);
  params.set("page", String(options.page ?? 1));
  params.set("page_size", String(options.pageSize ?? 20));
  return apiRequest<Page<Outreach>>(`/api/v1/outreach?${params.toString()}`);
}

export function prepareOutreach(data: OutreachPrepareRequest): Promise<Outreach> {
  return apiRequest<Outreach>("/api/v1/outreach/prepare", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function approveOutreach(outreachId: string): Promise<Outreach> {
  return apiRequest<Outreach>(`/api/v1/outreach/${outreachId}/approve`, {
    method: "POST",
  });
}

export function sendOutreach(outreachId: string): Promise<Outreach> {
  return apiRequest<Outreach>(`/api/v1/outreach/${outreachId}/send`, {
    method: "POST",
  });
}
