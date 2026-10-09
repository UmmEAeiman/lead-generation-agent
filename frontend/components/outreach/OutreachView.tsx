"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Modal } from "@/components/ui/Modal";
import { Pagination } from "@/components/ui/Pagination";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { Table, Td, Th } from "@/components/ui/Table";
import { useCampaigns } from "@/hooks/useCampaigns";
import { useLeads } from "@/hooks/useLeads";
import { useOutreach } from "@/hooks/useOutreach";
import { getErrorMessage } from "@/lib/api/client";
import {
  approveOutreach,
  prepareOutreach,
  sendOutreach,
} from "@/lib/api/outreach";
import { formatDate } from "@/lib/format";
import { OUTREACH_STATUS_META } from "@/lib/statusMeta";
import type { Outreach, OutreachStatus } from "@/types/outreach";

const STATUS_OPTIONS: Array<{ value: OutreachStatus | ""; label: string }> = [
  { value: "", label: "All statuses" },
  ...(
    Object.entries(OUTREACH_STATUS_META) as Array<[OutreachStatus, { label: string }]>
  ).map(([value, meta]) => ({ value, label: meta.label })),
];

const APPROVABLE: OutreachStatus[] = ["PREPARED", "PENDING_APPROVAL"];

export function OutreachView() {
  const [status, setStatus] = useState<OutreachStatus | "">("");
  const [page, setPage] = useState(1);
  const outreach = useOutreach({ status: status || undefined, page });
  const leads = useLeads({ page_size: 100, sort: "created_at", order: "desc" });
  const campaigns = useCampaigns();

  const [prepareOpen, setPrepareOpen] = useState(false);
  const [prepareLeadId, setPrepareLeadId] = useState("");
  const [prepareCampaignId, setPrepareCampaignId] = useState("");
  const [preparing, setPreparing] = useState(false);
  const [viewRecord, setViewRecord] = useState<Outreach | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [banner, setBanner] = useState<{ kind: "success" | "error"; text: string } | null>(
    null,
  );

  const items = outreach.data?.items ?? [];
  const leadItems = leads.data?.items ?? [];
  const campaignItems = campaigns.data?.items ?? [];
  const leadNames = new Map(leadItems.map((lead) => [lead.id, lead.company_name]));

  function nameFor(leadId: string): string {
    return leadNames.get(leadId) ?? `Lead ${leadId.slice(0, 8)}`;
  }

  async function onPrepare(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (preparing || !prepareLeadId) return;
    setPreparing(true);
    setBanner(null);
    try {
      await prepareOutreach({
        lead_id: prepareLeadId,
        campaign_id: prepareCampaignId || null,
      });
      setBanner({ kind: "success", text: "Outreach prepared for human approval." });
      setPrepareOpen(false);
      setPrepareLeadId("");
      setPrepareCampaignId("");
      outreach.reload();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setPreparing(false);
    }
  }

  async function act(record: Outreach, action: "approve" | "send") {
    if (busyId) return;
    setBusyId(record.id);
    setBanner(null);
    try {
      if (action === "approve") {
        await approveOutreach(record.id);
        setBanner({ kind: "success", text: "Outreach approved." });
      } else {
        await sendOutreach(record.id);
        setBanner({ kind: "success", text: "Outreach sent." });
      }
      outreach.reload();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
      outreach.reload();
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <p className="max-w-2xl text-sm text-muted">
          Every message requires human approval before it can be sent. Opted-out leads are
          never contacted.
        </p>
        <div className="flex items-end gap-3">
          <div className="w-52">
            <Select
              label="Status"
              value={status}
              onChange={(event) => {
                setStatus(event.target.value as OutreachStatus | "");
                setPage(1);
              }}
              options={STATUS_OPTIONS}
            />
          </div>
          <Button onClick={() => setPrepareOpen(true)}>Prepare outreach</Button>
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

      <Card>
        {outreach.loading ? (
          <div className="flex flex-col gap-3" aria-busy="true" aria-label="Loading outreach">
            {Array.from({ length: 5 }, (_, index) => (
              <Skeleton key={index} className="h-12" />
            ))}
          </div>
        ) : outreach.error ? (
          <ErrorState message={outreach.error} onRetry={outreach.reload} />
        ) : items.length === 0 ? (
          <EmptyState
            title="No outreach yet"
            description="Prepare a message for a lead to start the approval flow."
            action={<Button onClick={() => setPrepareOpen(true)}>Prepare outreach</Button>}
          />
        ) : (
          <>
            <Table>
              <thead>
                <tr>
                  <Th>Lead</Th>
                  <Th>Subject</Th>
                  <Th>Status</Th>
                  <Th>Created</Th>
                  <Th>Sent</Th>
                  <Th className="text-right">Actions</Th>
                </tr>
              </thead>
              <tbody>
                {items.map((record) => {
                  const meta = OUTREACH_STATUS_META[record.status];
                  return (
                    <tr key={record.id} className="hover:bg-muted-background/60">
                      <Td className="font-medium">{nameFor(record.lead_id)}</Td>
                      <Td className="max-w-64 truncate text-muted">
                        {record.subject || "(no subject)"}
                      </Td>
                      <Td>
                        <Badge tone={meta.tone}>{meta.label}</Badge>
                      </Td>
                      <Td className="text-muted">{formatDate(record.created_at)}</Td>
                      <Td className="text-muted">{formatDate(record.sent_at)}</Td>
                      <Td className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setViewRecord(record)}
                          >
                            View
                          </Button>
                          {APPROVABLE.includes(record.status) ? (
                            <Button
                              variant="secondary"
                              size="sm"
                              disabled={busyId === record.id}
                              onClick={() => void act(record, "approve")}
                            >
                              Approve
                            </Button>
                          ) : null}
                          {record.status === "APPROVED" ? (
                            <Button
                              variant="primary"
                              size="sm"
                              disabled={busyId === record.id}
                              loading={busyId === record.id}
                              onClick={() => void act(record, "send")}
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
            <Pagination
              page={page}
              pageSize={20}
              total={outreach.data?.total ?? 0}
              onPageChange={setPage}
            />
          </>
        )}
      </Card>

      <Modal
        open={prepareOpen}
        onClose={() => setPrepareOpen(false)}
        title="Prepare outreach"
        footer={
          <>
            <Button variant="secondary" onClick={() => setPrepareOpen(false)} disabled={preparing}>
              Cancel
            </Button>
            <Button
              type="submit"
              form="prepare-form"
              loading={preparing}
              disabled={!prepareLeadId}
            >
              Prepare
            </Button>
          </>
        }
      >
        <form id="prepare-form" onSubmit={onPrepare} className="flex flex-col gap-4">
          <Select
            label="Lead"
            required
            value={prepareLeadId}
            onChange={(event) => setPrepareLeadId(event.target.value)}
            placeholder="Choose a lead"
            options={leadItems.map((lead) => ({
              value: lead.id,
              label: lead.company_name,
            }))}
          />
          <Select
            label="Campaign (optional)"
            value={prepareCampaignId}
            onChange={(event) => setPrepareCampaignId(event.target.value)}
            placeholder="No campaign"
            options={campaignItems.map((campaign) => ({
              value: campaign.id,
              label: campaign.name,
            }))}
          />
        </form>
      </Modal>

      <Modal
        open={viewRecord !== null}
        onClose={() => setViewRecord(null)}
        wide
        title={viewRecord?.subject || "Outreach message"}
      >
        {viewRecord ? (
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted">
              <Badge tone={OUTREACH_STATUS_META[viewRecord.status].tone}>
                {OUTREACH_STATUS_META[viewRecord.status].label}
              </Badge>
              <span>{nameFor(viewRecord.lead_id)}</span>
              <span>·</span>
              <span>{viewRecord.channel}</span>
            </div>
            {viewRecord.error ? (
              <p className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger">
                {viewRecord.error}
              </p>
            ) : null}
            <pre className="whitespace-pre-wrap rounded-md bg-muted-background p-4 text-sm text-foreground">
              {viewRecord.body}
            </pre>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
