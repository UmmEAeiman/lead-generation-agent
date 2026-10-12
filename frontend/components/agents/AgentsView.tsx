"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { useCampaigns } from "@/hooks/useCampaigns";
import { useRuns } from "@/hooks/useRuns";
import { queueRun } from "@/lib/api/agents";
import { getErrorMessage } from "@/lib/api/client";
import { formatDate } from "@/lib/format";
import { AGENT_TYPE_LABELS, RUN_STATUS_META } from "@/lib/statusMeta";
import type { AgentRun, AgentType, IcpInput } from "@/types/agent";

const LAUNCHABLE_AGENTS: Array<{ value: AgentType; label: string }> = [
  { value: "discovery", label: "Discovery — find new leads for an ICP" },
  { value: "pipeline", label: "Full pipeline — discover, enrich, research, qualify" },
];

interface LaunchFormState {
  agentType: AgentType;
  campaignId: string;
  industry: string;
  location: string;
  companySize: string;
  keywords: string;
  limit: string;
}

const INITIAL_FORM: LaunchFormState = {
  agentType: "discovery",
  campaignId: "",
  industry: "",
  location: "",
  companySize: "",
  keywords: "",
  limit: "",
};

function progressPercent(run: AgentRun): number {
  if (run.status === "completed") return 100;
  if (typeof run.progress === "number") return Math.max(0, Math.min(100, run.progress));
  if (run.status === "queued") return 0;
  return 15;
}

export function AgentsView() {
  const router = useRouter();
  const runs = useRuns(1, 3000);
  const campaigns = useCampaigns();
  const [form, setForm] = useState<LaunchFormState>(INITIAL_FORM);
  const [launching, setLaunching] = useState(false);
  const [banner, setBanner] = useState<{ kind: "success" | "error"; text: string } | null>(
    null,
  );
  const [detailsRun, setDetailsRun] = useState<AgentRun | null>(null);

  const runItems = runs.data?.items ?? [];
  const campaignItems = campaigns.data?.items ?? [];
  const hasActiveRun = runItems.some(
    (run) => run.status === "queued" || run.status === "running",
  );

  async function onLaunch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (launching) return;

    setLaunching(true);
    setBanner(null);

    const icp: IcpInput = {
      industry: form.industry.trim() || undefined,
      location: form.location.trim() || undefined,
      company_size: form.companySize.trim() || undefined,
      keywords: form.keywords
        .split(",")
        .map((word) => word.trim())
        .filter(Boolean),
    };

    try {
      const parsedLimit = Number.parseInt(form.limit, 10);
      const run = await queueRun(form.agentType, {
        campaign_id: form.campaignId || null,
        icp,
        limit: Number.isFinite(parsedLimit) ? parsedLimit : null,
      });
      setBanner({
        kind: "success",
        text: `${AGENT_TYPE_LABELS[form.agentType]} run queued (${run.run_id}).`,
      });
      runs.reload();
      router.refresh();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setLaunching(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-muted">
        Queue background runs. For enrichment, research, qualification, personalization,
        and follow-up, select leads on the{" "}
        <Link href="/dashboard/leads" className="text-primary hover:underline">
          Leads
        </Link>{" "}
        page and use the bulk actions.
      </p>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Launch an agent" description="Discovery and full-pipeline runs">
          <form onSubmit={onLaunch} className="flex flex-col gap-4" noValidate>
            {banner ? (
              <div
                role="status"
                className={`rounded-md px-3 py-2 text-sm ${
                  banner.kind === "success"
                    ? "bg-success/10 text-success"
                    : "bg-danger/10 text-danger"
                }`}
              >
                {banner.text}
              </div>
            ) : null}
            <Select
              label="Agent"
              value={form.agentType}
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  agentType: event.target.value as AgentType,
                }))
              }
              options={LAUNCHABLE_AGENTS}
            />
            <Select
              label="Campaign (optional)"
              value={form.campaignId}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, campaignId: event.target.value }))
              }
              placeholder="Use manual ICP below"
              options={campaignItems.map((campaign) => ({
                value: campaign.id,
                label: campaign.name,
              }))}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              <Input
                label="ICP industry"
                value={form.industry}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, industry: event.target.value }))
                }
                placeholder="SaaS"
              />
              <Input
                label="ICP location"
                value={form.location}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, location: event.target.value }))
                }
                placeholder="United States"
              />
              <Input
                label="ICP company size"
                value={form.companySize}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, companySize: event.target.value }))
                }
                placeholder="11-50"
              />
              <Input
                label="ICP keywords"
                value={form.keywords}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, keywords: event.target.value }))
                }
                placeholder="funding, hiring (comma-separated)"
              />
              <Input
                label="Leads per run (capacity)"
                type="number"
                min={1}
                max={50}
                inputMode="numeric"
                value={form.limit}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, limit: event.target.value }))
                }
                placeholder="Default 20 · max 50"
              />
            </div>
            <Button type="submit" loading={launching}>
              Queue run
            </Button>
          </form>
        </Card>

        <Card
          title="Runs"
          description={
            hasActiveRun
              ? "Refreshing every 3 seconds while runs are active"
              : "All runs, newest first"
          }
        >
          {runs.loading ? (
            <div className="flex flex-col gap-3" aria-busy="true" aria-label="Loading runs">
              {Array.from({ length: 4 }, (_, index) => (
                <Skeleton key={index} className="h-14" />
              ))}
            </div>
          ) : runs.error ? (
            <ErrorState message={runs.error} onRetry={runs.reload} />
          ) : runItems.length === 0 ? (
            <EmptyState
              title="No runs yet"
              description="Queue your first agent run to see progress here."
            />
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {runItems.map((run) => {
                const meta = RUN_STATUS_META[run.status];
                const percent = progressPercent(run);
                return (
                  <li key={run.run_id} className="py-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <p className="text-sm font-medium text-foreground">
                          {AGENT_TYPE_LABELS[run.agent_type]}
                        </p>
                        <p className="text-xs text-muted">
                          {run.run_id}
                          {run.started_at ? ` · ${formatDate(run.started_at)}` : ""}
                          {run.duration !== null ? ` · ${run.duration.toFixed(1)}s` : ""}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge tone={meta.tone}>{meta.label}</Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDetailsRun(run)}
                        >
                          Details
                        </Button>
                      </div>
                    </div>
                    <div
                      role="progressbar"
                      aria-valuenow={percent}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={`${AGENT_TYPE_LABELS[run.agent_type]} progress`}
                      className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-muted-background"
                    >
                      <div
                        className={`h-full rounded-full ${
                          run.status === "failed" ? "bg-danger" : "bg-primary"
                        }`}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    {run.error ? (
                      <p className="mt-1 text-xs text-danger">{run.error}</p>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          )}
        </Card>
      </div>

      <Modal
        open={detailsRun !== null}
        onClose={() => setDetailsRun(null)}
        wide
        title={
          detailsRun ? `${AGENT_TYPE_LABELS[detailsRun.agent_type]} · ${detailsRun.run_id}` : ""
        }
      >
        {detailsRun ? (
          <div className="flex flex-col gap-4">
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-xs font-semibold uppercase text-muted">Status</dt>
                <dd>
                  <Badge tone={RUN_STATUS_META[detailsRun.status].tone}>
                    {RUN_STATUS_META[detailsRun.status].label}
                  </Badge>
                </dd>
              </div>
              <div>
                <dt className="text-xs font-semibold uppercase text-muted">Tokens used</dt>
                <dd>{detailsRun.tokens_used ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold uppercase text-muted">Started</dt>
                <dd>{formatDate(detailsRun.started_at)}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold uppercase text-muted">Completed</dt>
                <dd>{formatDate(detailsRun.completed_at)}</dd>
              </div>
            </dl>
            {detailsRun.error ? (
              <p className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger">
                {detailsRun.error}
              </p>
            ) : null}
            <div>
              <p className="mb-1 text-xs font-semibold uppercase text-muted">Input</p>
              <pre className="overflow-x-auto rounded-md bg-muted-background p-3 text-xs text-foreground">
                {JSON.stringify(detailsRun.input_summary, null, 2)}
              </pre>
            </div>
            <div>
              <p className="mb-1 text-xs font-semibold uppercase text-muted">Output</p>
              <pre className="overflow-x-auto rounded-md bg-muted-background p-3 text-xs text-foreground">
                {Object.keys(detailsRun.output_summary).length > 0
                  ? JSON.stringify(detailsRun.output_summary, null, 2)
                  : "No output yet."}
              </pre>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
