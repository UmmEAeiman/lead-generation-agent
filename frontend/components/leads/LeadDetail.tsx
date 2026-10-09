"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { LeadForm } from "@/components/leads/LeadForm";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { getErrorMessage } from "@/lib/api/client";
import { deleteLead, getLead, optOutLead, updateLead } from "@/lib/api/leads";
import { prepareOutreach } from "@/lib/api/outreach";
import { formatDate } from "@/lib/format";
import { useAsync } from "@/hooks/useAsync";
import { useOutreach } from "@/hooks/useOutreach";
import {
  FOLLOWUP_STATE_LABELS,
  LEAD_STATUSES,
  LEAD_STATUS_META,
  OUTREACH_STATUS_META,
  QUALIFICATION_META,
} from "@/lib/statusMeta";
import type { LeadStatus } from "@/types/lead";

function Row({
  label,
  value,
  children,
}: {
  label: string;
  value?: string | null;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-0.5 py-2">
      <dt className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</dt>
      <dd className="text-sm text-foreground">{children ?? value ?? "—"}</dd>
    </div>
  );
}

function ExternalOrText({ value, href }: { value: string | null; href?: string }) {
  if (!value) return <span>—</span>;
  if (!href) return <span>{value}</span>;
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-primary hover:underline"
    >
      {value}
    </a>
  );
}

export function LeadDetail({ leadId }: { leadId: string }) {
  const router = useRouter();
  const { data: lead, loading, error, reload } = useAsync(
    () => getLead(leadId),
    [leadId],
  );
  const outreach = useOutreach({ leadId });

  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [optOutOpen, setOptOutOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [banner, setBanner] = useState<{ kind: "success" | "error"; text: string } | null>(
    null,
  );

  async function changeStatus(next: LeadStatus) {
    if (!lead || next === lead.status || busy) return;
    setBusy(true);
    setBanner(null);
    try {
      await updateLead(lead.id, { status: next });
      setBanner({ kind: "success", text: `Status changed to ${LEAD_STATUS_META[next].label}.` });
      reload();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
      reload();
    } finally {
      setBusy(false);
    }
  }

  async function onPrepareOutreach() {
    if (busy) return;
    setBusy(true);
    setBanner(null);
    try {
      await prepareOutreach({ lead_id: leadId });
      setBanner({
        kind: "success",
        text: "Outreach prepared and queued for human approval.",
      });
      outreach.reload();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setBusy(false);
    }
  }

  async function onDelete() {
    if (busy) return;
    setBusy(true);
    try {
      await deleteLead(leadId);
      router.push("/dashboard/leads");
      router.refresh();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
      setBusy(false);
      setDeleteOpen(false);
    }
  }

  async function onOptOut() {
    if (busy) return;
    setBusy(true);
    try {
      await optOutLead(leadId);
      setBanner({ kind: "success", text: "Lead marked do-not-contact." });
      setOptOutOpen(false);
      reload();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col gap-4" aria-busy="true" aria-label="Loading lead">
        <Skeleton className="h-10 w-72" />
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-56" />
          <Skeleton className="h-56" />
          <Skeleton className="h-56" />
          <Skeleton className="h-56" />
        </div>
      </div>
    );
  }

  if (error || !lead) {
    return <ErrorState message={error ?? "Lead not found."} onRetry={reload} />;
  }

  const statusMeta = LEAD_STATUS_META[lead.status];
  const qualification = QUALIFICATION_META[lead.qualification];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link
            href="/dashboard/leads"
            className="text-sm text-muted hover:text-foreground"
          >
            ← Back to leads
          </Link>
          <h1 className="mt-1 text-xl font-semibold text-foreground">
            {lead.company_name}
          </h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Badge tone={statusMeta.tone}>{statusMeta.label}</Badge>
            <Badge tone={qualification.tone}>{qualification.label} qualification</Badge>
            {lead.lead_score !== null ? (
              <Badge tone="info">Score {lead.lead_score}</Badge>
            ) : null}
            {lead.followup_state ? (
              <Badge tone="neutral">
                {FOLLOWUP_STATE_LABELS[lead.followup_state]}
              </Badge>
            ) : null}
          </div>
        </div>
        <div className="flex flex-wrap items-end gap-2">
          <div className="w-48">
            <Select
              label="Status"
              value={lead.status}
              disabled={busy}
              onChange={(event) => void changeStatus(event.target.value as LeadStatus)}
              options={LEAD_STATUSES.map((value) => ({
                value,
                label: LEAD_STATUS_META[value].label,
              }))}
            />
          </div>
          <Button variant="secondary" onClick={() => setEditOpen(true)}>
            Edit
          </Button>
          <Button variant="secondary" onClick={() => void onPrepareOutreach()} loading={busy}>
            Prepare outreach
          </Button>
          <Button variant="secondary" onClick={() => setOptOutOpen(true)}>
            Opt out
          </Button>
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            Delete
          </Button>
        </div>
      </div>

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

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Company information">
          <dl className="divide-y divide-border">
            <Row label="Website">
              <ExternalOrText value={lead.website} href={lead.website ?? undefined} />
            </Row>
            <Row label="Industry" value={lead.industry} />
            <Row label="Location" value={lead.location} />
            <Row label="Company size" value={lead.company_size} />
            <Row label="Source" value={lead.source} />
            <Row label="Description" value={lead.description} />
          </dl>
        </Card>

        <Card title="Contact information">
          <dl className="divide-y divide-border">
            <Row label="Contact name" value={lead.contact_name} />
            <Row label="Role" value={lead.contact_role} />
            <Row label="Email">
              {lead.email ? (
                <a href={`mailto:${lead.email}`} className="text-primary hover:underline">
                  {lead.email}
                </a>
              ) : (
                "—"
              )}
            </Row>
            <Row label="Phone" value={lead.phone} />
            <Row label="LinkedIn">
              <ExternalOrText
                value={lead.linkedin_url}
                href={lead.linkedin_url ?? undefined}
              />
            </Row>
          </dl>
        </Card>

        <Card title="Score & qualification">
          <div className="mb-3 flex items-center gap-3">
            <span className="text-3xl font-semibold text-foreground">
              {lead.lead_score ?? "—"}
            </span>
            <Badge tone={qualification.tone}>{qualification.label}</Badge>
          </div>
          {lead.qualification_reasons.length > 0 ? (
            <ul className="flex list-disc flex-col gap-1 pl-5 text-sm text-muted">
              {lead.qualification_reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted">
              No qualification reasons yet. Run the qualification agent to score this lead.
            </p>
          )}
        </Card>

        <Card title="AI research">
          {lead.research_summary ? (
            <p className="text-sm leading-relaxed text-muted">{lead.research_summary}</p>
          ) : (
            <p className="text-sm text-muted">
              No research yet. Run the research agent to enrich this lead.
            </p>
          )}
          {lead.pain_points.length > 0 ? (
            <>
              <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-muted">
                Pain points
              </p>
              <ul className="mt-1 flex list-disc flex-col gap-1 pl-5 text-sm text-foreground">
                {lead.pain_points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </>
          ) : null}
        </Card>

        <Card title="Personalized message">
          {lead.personalized_message ? (
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
              {lead.personalized_message}
            </p>
          ) : (
            <p className="text-sm text-muted">
              No message drafted yet. Run the personalization agent.
            </p>
          )}
        </Card>

        <Card title="Outreach">
          {outreach.loading ? (
            <Skeleton className="h-24" />
          ) : outreach.error ? (
            <ErrorState message={outreach.error} onRetry={outreach.reload} />
          ) : (outreach.data?.items.length ?? 0) === 0 ? (
            <EmptyState
              title="No outreach yet"
              description="Prepare an outreach message to start the approval flow."
            />
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {outreach.data?.items.map((record) => {
                const meta = OUTREACH_STATUS_META[record.status];
                return (
                  <li key={record.id} className="flex items-start justify-between gap-3 py-3">
                    <div>
                      <p className="text-sm font-medium text-foreground">
                        {record.subject || "(no subject)"}
                      </p>
                      <p className="text-xs text-muted">
                        {record.channel} · {formatDate(record.created_at)}
                      </p>
                    </div>
                    <Badge tone={meta.tone}>{meta.label}</Badge>
                  </li>
                );
              })}
            </ul>
          )}
        </Card>
      </div>

      <Card title="Activity">
        <dl className="divide-y divide-border">
          <Row label="Created" value={formatDate(lead.created_at)} />
          <Row label="Last updated" value={formatDate(lead.updated_at)} />
          <Row label="Follow-up state" value={
            lead.followup_state ? FOLLOWUP_STATE_LABELS[lead.followup_state] : null
          } />
        </dl>
      </Card>

      {editOpen ? (
        <LeadForm
          open
          lead={lead}
          onClose={() => setEditOpen(false)}
          onSaved={() => {
            setEditOpen(false);
            reload();
          }}
        />
      ) : null}
      <ConfirmDialog
        open={deleteOpen}
        title="Delete lead"
        message={`Delete ${lead.company_name} permanently? This cannot be undone.`}
        confirmLabel="Delete"
        danger
        busy={busy}
        onConfirm={() => void onDelete()}
        onCancel={() => setDeleteOpen(false)}
      />
      <ConfirmDialog
        open={optOutOpen}
        title="Opt out lead"
        message="Mark this lead as do-not-contact? All automated outreach stops permanently."
        confirmLabel="Opt out"
        danger
        busy={busy}
        onConfirm={() => void onOptOut()}
        onCancel={() => setOptOutOpen(false)}
      />
    </div>
  );
}
