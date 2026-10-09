import { apiRequest } from "@/lib/api/client";
import type { Page } from "@/types/api";
import type { AgentRun, AgentRunRequest, QueuedRun } from "@/types/agent";

export function queueRun(
  agentType: string,
  data: AgentRunRequest = {},
): Promise<QueuedRun> {
  return apiRequest<QueuedRun>(`/api/v1/agents/${agentType}/run`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function listRuns(page = 1, pageSize = 20): Promise<Page<AgentRun>> {
  return apiRequest<Page<AgentRun>>(
    `/api/v1/agents/runs?page=${page}&page_size=${pageSize}`,
  );
}

export function getRun(runId: string): Promise<AgentRun> {
  return apiRequest<AgentRun>(`/api/v1/agents/runs/${runId}`);
}
