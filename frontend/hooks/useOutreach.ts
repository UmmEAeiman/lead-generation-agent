"use client";

import { useAsync } from "@/hooks/useAsync";
import { listOutreach } from "@/lib/api/outreach";
import type { Page } from "@/types/api";
import type { Outreach } from "@/types/outreach";

export function useOutreach(options: {
  status?: string;
  leadId?: string;
  run_id?: string;
  campaign_id?: string;
  page?: number;
  pollMs?: number;
}) {
  return useAsync<Page<Outreach>>(
    () =>
      listOutreach({
        status: options.status,
        leadId: options.leadId,
        run_id: options.run_id,
        campaign_id: options.campaign_id,
        page: options.page,
        pageSize: 20,
      }),
    [options.status, options.leadId, options.run_id, options.campaign_id, options.page],
    { pollMs: options.pollMs },
  );
}
