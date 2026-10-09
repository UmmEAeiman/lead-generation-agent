"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { CampaignForm } from "@/components/campaigns/CampaignForm";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Dropdown } from "@/components/ui/Dropdown";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Skeleton } from "@/components/ui/Skeleton";
import { Table, Td, Th } from "@/components/ui/Table";
import { useCampaigns } from "@/hooks/useCampaigns";
import { queueRun } from "@/lib/api/agents";
import { getErrorMessage } from "@/lib/api/client";
import { updateCampaign } from "@/lib/api/campaigns";
import { CAMPAIGN_STATUS_META } from "@/lib/statusMeta";
import type { Campaign, CampaignStatus } from "@/types/campaign";

const STATUS_ACTIONS: Array<{ label: string; status: CampaignStatus }> = [
  { label: "Mark active", status: "ACTIVE" },
  { label: "Pause", status: "PAUSED" },
  { label: "Mark completed", status: "COMPLETED" },
  { label: "Move to draft", status: "DRAFT" },
];

export function CampaignsView() {
  const router = useRouter();
  const { data, loading, error, reload } = useCampaigns();
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Campaign | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [banner, setBanner] = useState<{ kind: "success" | "error"; text: string } | null>(
    null,
  );

  const items = data?.items ?? [];

  async function changeStatus(campaign: Campaign, status: CampaignStatus) {
    if (busyId) return;
    setBusyId(campaign.id);
    setBanner(null);
    try {
      await updateCampaign(campaign.id, { status });
      reload();
      router.refresh();
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setBusyId(null);
    }
  }

  async function runDiscovery(campaign: Campaign) {
    if (busyId) return;
    setBusyId(campaign.id);
    setBanner(null);
    try {
      const run = await queueRun("discovery", { campaign_id: campaign.id });
      setBanner({
        kind: "success",
        text: `Discovery queued for “${campaign.name}” (${run.run_id}).`,
      });
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted">
          Campaigns group your ideal customer profile for discovery and tracking.
        </p>
        <Button
          onClick={() => {
            setEditing(null);
            setFormOpen(true);
          }}
        >
          New campaign
        </Button>
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
        {loading ? (
          <div className="flex flex-col gap-3" aria-busy="true" aria-label="Loading campaigns">
            {Array.from({ length: 4 }, (_, index) => (
              <Skeleton key={index} className="h-14" />
            ))}
          </div>
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : items.length === 0 ? (
          <EmptyState
            title="No campaigns yet"
            description="Create a campaign to define your ideal customer profile."
            action={
              <Button
                onClick={() => {
                  setEditing(null);
                  setFormOpen(true);
                }}
              >
                New campaign
              </Button>
            }
          />
        ) : (
          <Table>
            <thead>
              <tr>
                <Th>Name</Th>
                <Th>Status</Th>
                <Th>Target</Th>
                <Th>Keywords</Th>
                <Th>Created</Th>
                <Th className="text-right">Actions</Th>
              </tr>
            </thead>
            <tbody>
              {items.map((campaign) => {
                const meta = CAMPAIGN_STATUS_META[campaign.status];
                const targets = [
                  campaign.target_industry,
                  campaign.target_location,
                  campaign.target_company_size,
                ]
                  .filter(Boolean)
                  .join(" · ");
                return (
                  <tr key={campaign.id} className="hover:bg-muted-background/60">
                    <Td>
                      <p className="font-medium text-foreground">{campaign.name}</p>
                      {campaign.description ? (
                        <p className="max-w-md truncate text-xs text-muted">
                          {campaign.description}
                        </p>
                      ) : null}
                    </Td>
                    <Td>
                      <Badge tone={meta.tone}>{meta.label}</Badge>
                    </Td>
                    <Td className="text-muted">{targets || "—"}</Td>
                    <Td>
                      <div className="flex flex-wrap gap-1">
                        {campaign.keywords.length > 0 ? (
                          campaign.keywords.map((keyword) => (
                            <Badge key={keyword} tone="neutral">
                              {keyword}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-muted">—</span>
                        )}
                      </div>
                    </Td>
                    <Td className="text-muted">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </Td>
                    <Td className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          disabled={busyId === campaign.id}
                          onClick={() => void runDiscovery(campaign)}
                        >
                          Run discovery
                        </Button>
                        <Dropdown
                          label="More"
                          items={[
                            {
                              label: "Edit",
                              onSelect: () => {
                                setEditing(campaign);
                                setFormOpen(true);
                              },
                            },
                            ...STATUS_ACTIONS.filter(
                              (action) => action.status !== campaign.status,
                            ).map((action) => ({
                              label: action.label,
                              onSelect: () => void changeStatus(campaign, action.status),
                            })),
                          ]}
                        />
                      </div>
                    </Td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        )}
      </Card>

      {formOpen ? (
        <CampaignForm
          open
          campaign={editing}
          onClose={() => setFormOpen(false)}
          onSaved={() => {
            setFormOpen(false);
            setEditing(null);
            reload();
            router.refresh();
          }}
        />
      ) : null}
    </div>
  );
}
