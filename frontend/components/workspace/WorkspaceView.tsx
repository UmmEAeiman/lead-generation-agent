"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { Table, Td, Th } from "@/components/ui/Table";
import { useLeads } from "@/hooks/useLeads";
import { useOutreach } from "@/hooks/useOutreach";
import { useRuns } from "@/hooks/useRuns";
import { getErrorMessage } from "@/lib/api/client";
import { approveOutreach, sendOutreach } from "@/lib/api/outreach";
import { formatDate } from "@/lib/format";
import {
  AGENT_TYPE_LABELS,
  LEAD_STATUS_META,
  OUTREACH_STATUS_META,
  RUN_STATUS_META,
} from "@/lib/statusMeta";
import type { Lead } from "@/types/lead";
import type { Outreach } from "@/types/outreach";

const APPROVABLE: string[] = ["PREPARED", "PENDING_APPROVAL"];

interface Props {
  initialRunId?: string;
}

export function WorkspaceView({ initialRunId = "" }: Props) {
  const [selectedRunId, setSelectedRunId] = useState(initialRunId);
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [busyId, setBusyId] = useState<string | null>(null);
  const [banner, setBanner] = useState<{ kind: "success" | "error"; text: string } | null>(null);

  const runs = useRuns(1);
  const runItems = useMemo(() => runs.data?.items ?? [], [runs.data?.items]);
  const firstRunId = runItems[0]?.run_id ?? "";
  const runId = selectedRunId || firstRunId;
  const leads = useLeads({ run_id: runId || undefined, page_size: 100, sort: "created_at", order: "desc" });
  const leadItems = useMemo(() => leads.data?.items ?? [], [leads.data?.items]);
  const outreach = useOutreach({ run_id: runId || undefined, page, pageSize: 20 });
  const outreachItems = useMemo(() => outreach.data?.items ?? [], [outreach.data?.items]);

  const leadMap = useMemo(() => new Map<string, Lead>(leadItems.map((lead) => [lead.id, lead])), [leadItems]);
  const selectedOutreach = outreachItems.filter((item) => selected.has(item.id));

  function toggleSelected(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleSelectAll() {
    setSelected((prev) =>
      prev.size === outreachItems.length && outreachItems.length > 0
        ? new Set()
        : new Set(outreachItems.map((item) => item.id)),
    );
  }

  async function actOne(item: Outreach, action: "approve" | "send") {
    if (busyId) return;
    setBusyId(item.id);
    setBanner(null);
    try {
      if (action === "approve") {
        await approveOutreach(item.id);
        setBanner({ kind: "success", text: "Outreach approved." });
      } else {
        await sendOutreach(item.id);
        setBanner({ kind: "success", text: "Outreach sent." });
      }
      outreach.reload();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setBusyId(null);
    }
  }

  async function bulkApproveAll() {
    if (busyId || selectedOutreach.length === 0) return;
    setBusyId("bulk");
    setBanner(null);
    try {
      for (const item of selectedOutreach) {
        if (APPROVABLE.includes(item.status)) {
          await approveOutreach(item.id);
        }
      }
      setBanner({ kind: "success", text: "Approved selected drafts." });
      setSelected(new Set());
      outreach.reload();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setBusyId(null);
    }
  }

  async function bulkSendAll() {
    if (busyId || selectedOutreach.length === 0) return;
    setBusyId("bulk");
    setBanner(null);
    try {
      for (const item of selectedOutreach) {
        if (item.status === "APPROVED") {
          await sendOutreach(item.id);
        }
      }
      setBanner({ kind: "success", text: "Sent approved selected." });
      setSelected(new Set());
      outreach.reload();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setBusyId(null);
    }
  }

  const allSelected = outreachItems.length > 0 && selected.size === outreachItems.length;
  const run = runItems.find((r) => r.run_id === runId) || null;

  return (
    <div className="flex flex-col gap-4">
      <Card
        title="Pick a run"
        description="A run is one job you launched from the AI Agents page. Pick it here to see the leads it found and the outreach drafts it created."
      >
        {runs.error ? (
          <ErrorState message={runs.error} onRetry={runs.reload} />
        ) : runs.loading ? (
          <Skeleton className="h-12" />
        ) : runItems.length === 0 ? (
          <EmptyState
            title="No runs yet"
            description="Launch a discovery or full-pipeline run from the AI Agents page. Its leads and drafts will show up here."
            action={
              <Link href="/dashboard/agents">
                <Button>Go to AI Agents</Button>
              </Link>
            }
          />
        ) : (
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap items-end gap-3">
              <div className="min-w-64 flex-1">
                <Select
                  label="Run"
                  value={runId}
                  onChange={(e) => {
                    setSelectedRunId(e.target.value);
                    setPage(1);
                    setSelected(new Set());
                  }}
                  placeholder="Select a run"
                  options={runItems.map((r) => ({
                    value: r.run_id,
                    label: `${AGENT_TYPE_LABELS[r.agent_type]} · ${formatDate(r.started_at)} · ${RUN_STATUS_META[r.status].label}`,
                  }))}
                />
              </div>
              <Button variant="ghost" size="sm" onClick={runs.reload}>
                Refresh
              </Button>
            </div>
            {run ? (
              <div className="grid gap-2 text-xs text-muted sm:grid-cols-2 md:grid-cols-4">
                <div>
                  <span className="font-semibold text-foreground">Status:</span>{" "}
                  <Badge tone={RUN_STATUS_META[run.status].tone}>
                    {RUN_STATUS_META[run.status].label}
                  </Badge>
                </div>
                <div>
                  <span className="font-semibold text-foreground">Agent:</span>{" "}
                  {AGENT_TYPE_LABELS[run.agent_type]}
                </div>
                <div>
                  <span className="font-semibold text-foreground">Completed:</span>{" "}
                  {formatDate(run.completed_at)}
                </div>
                <div>
                  <span className="font-semibold text-foreground">Leads found:</span>{" "}
                  {leadItems.length}
                </div>
              </div>
            ) : null}
          </div>
        )}
      </Card>

      {banner ? (
        <div
          role="status"
          className={`rounded-md px-3 py-2 text-sm ${
            banner.kind === "success" ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
          }`}
        >
          {banner.text}
        </div>
      ) : null}

      <Card title="Leads from this run" description="Leads created/targeted by the selected run">
        {leads.loading ? (
          <div className="flex flex-col gap-3" aria-busy="true">
            {Array.from({ length: 4 }, (_, i) => (
              <Skeleton key={i} className="h-10" />
            ))}
          </div>
        ) : leads.error ? (
          <ErrorState message={leads.error} onRetry={leads.reload} />
        ) : leadItems.length === 0 ? (
          <EmptyState
            title="No linked leads for this run"
            description="Leads are linked to the run that created them. Runs launched before run tracking won't show linked leads. Launch a new run from AI Agents to see results here."
          />
        ) : (
          <Table>
            <thead>
              <tr>
                <Th>Company</Th>
                <Th>Status</Th>
                <Th>Email</Th>
                <Th>Qualified</Th>
                <Th>Personalized</Th>
                <Th>Run</Th>
              </tr>
            </thead>
            <tbody>
              {leadItems.map((lead) => {
                const statusMeta = LEAD_STATUS_META[lead.status];
                return (
                  <tr key={lead.id} className="hover:bg-muted-background/60">
                    <Td>
                      <Link href={`/dashboard/leads/${lead.id}`} className="font-medium text-foreground hover:underline">
                        {lead.company_name}
                      </Link>
                    </Td>
                    <Td>
                      <Badge tone={statusMeta.tone}>{statusMeta.label}</Badge>
                    </Td>
                    <Td className="text-muted">{lead.email ?? "—"}</Td>
                    <Td className="text-muted">{lead.status === "QUALIFIED" ? "Yes" : "No"}</Td>
                    <Td className="text-muted">{lead.personalized_message ? "Yes" : "No"}</Td>
                    <Td className="text-muted">{lead.run_id ?? "—"}</Td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        )}
      </Card>

      <Card
        title="Outreach drafts"
        description="Review each message, then Approve and Send. Sending always requires your approval first."
        actions={
          <>
            <Button
              variant="secondary"
              size="sm"
              disabled={busyId !== null || selectedOutreach.length === 0}
              onClick={() => void bulkApproveAll()}
            >
              Approve selected
            </Button>
            <Button
              variant="primary"
              size="sm"
              disabled={busyId !== null || selectedOutreach.length === 0}
              onClick={() => void bulkSendAll()}
            >
              Send selected
            </Button>
          </>
        }
      >
        {outreach.loading ? (
          <div className="flex flex-col gap-3" aria-busy="true">
            {Array.from({ length: 4 }, (_, i) => (
              <Skeleton key={i} className="h-10" />
            ))}
          </div>
        ) : outreach.error ? (
          <ErrorState message={outreach.error} onRetry={outreach.reload} />
        ) : outreachItems.length === 0 ? (
          <EmptyState
            title="No outreach drafts for this run"
            description="Run pipeline with auto-drafts enabled, or prepare outreach for leads."
          />
        ) : (
          <>
            <Table>
              <thead>
                <tr>
                  <Th className="w-10">
                    <input
                      type="checkbox"
                      aria-label="Select all"
                      checked={allSelected}
                      onChange={toggleSelectAll}
                    />
                  </Th>
                  <Th>Lead</Th>
                  <Th>Status</Th>
                  <Th>Created</Th>
                  <Th>Sent</Th>
                  <Th className="text-right">Actions</Th>
                </tr>
              </thead>
              <tbody>
                {outreachItems.map((item) => {
                  const meta = OUTREACH_STATUS_META[item.status];
                  const lead = leadMap.get(item.lead_id);
                  return (
                    <tr key={item.id} className="hover:bg-muted-background/60">
                      <Td>
                        <input
                          type="checkbox"
                          checked={selected.has(item.id)}
                          onChange={() => toggleSelected(item.id)}
                        />
                      </Td>
                      <Td className="font-medium">{lead?.company_name ?? `Lead ${item.lead_id.slice(0, 8)}`}</Td>
                      <Td>
                        <Badge tone={meta.tone}>{meta.label}</Badge>
                      </Td>
                      <Td className="text-muted">{formatDate(item.created_at)}</Td>
                      <Td className="text-muted">{formatDate(item.sent_at)}</Td>
                      <Td className="text-right">
                        <div className="flex justify-end gap-2">
                          {APPROVABLE.includes(item.status) ? (
                            <Button
                              variant="secondary"
                              size="sm"
                              disabled={busyId === item.id}
                              onClick={() => void actOne(item, "approve")}
                            >
                              Approve
                            </Button>
                          ) : null}
                          {item.status === "APPROVED" ? (
                            <Button
                              variant="primary"
                              size="sm"
                              disabled={busyId === item.id}
                              loading={busyId === item.id}
                              onClick={() => void actOne(item, "send")}
                            >
                              Send
                            </Button>
                          ) : null}
                        </div>
                      </Td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>
          </>
        )}
      </Card>
    </div>
  );
}


