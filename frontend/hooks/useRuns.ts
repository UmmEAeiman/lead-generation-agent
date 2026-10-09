"use client";

import { useAsync } from "@/hooks/useAsync";
import { listRuns } from "@/lib/api/agents";
import type { Page } from "@/types/api";
import type { AgentRun } from "@/types/agent";

export function useRuns(page = 1, pollMs?: number) {
  return useAsync<Page<AgentRun>>(() => listRuns(page, 20), [page], {
    pollMs,
  });
}
