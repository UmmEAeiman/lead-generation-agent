"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";

import { LeadForm } from "@/components/leads/LeadForm";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Checkbox } from "@/components/ui/Checkbox";
import { Dropdown } from "@/components/ui/Dropdown";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Pagination } from "@/components/ui/Pagination";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { Table, Td, Th } from "@/components/ui/Table";
import { useDebounce } from "@/hooks/useDebounce";
import { useLeads } from "@/hooks/useLeads";
import { queueRun } from "@/lib/api/agents";
import { getErrorMessage } from "@/lib/api/client";
import { exportLeads } from "@/lib/api/leads";
import { LEAD_STATUSES, LEAD_STATUS_META, QUALIFICATION_META } from "@/lib/statusMeta";
import type { AgentType } from "@/types/agent";
import type { Lead, LeadFilters, LeadStatus } from "@/types/lead";

const BULK_AGENTS: Array<{ id: AgentType; label: string }> = [
  { id: "enrichment", label: "Enrich selected" },
  { id: "research", label: "Research selected" },
  { id: "qualification", label: "Qualify selected" },
  { id: "personalization", label: "Personalize selected" },
  { id: "followup", label: "Follow up selected" },
];

const SORT_OPTIONS = [
  { value: "created_at", label: "Newest first" },
  { value: "lead_score", label: "Highest score" },
  { value: "updated_at", label: "Recently updated" },
];

export function LeadsView({ initialQuery = "" }: { initialQuery?: string }) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [status, setStatus] = useState<LeadStatus | "">("");
  const [industry, setIndustry] = useState("");
  const [location, setLocation] = useState("");
  const [scoreMin, setScoreMin] = useState("");
  const [scoreMax, setScoreMax] = useState("");
  const [sort, setSort] = useState("created_at");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [formOpen, setFormOpen] = useState(false);
  const [banner, setBanner] = useState<{ kind: "success" | "error"; text: string } | null>(
    null,
  );
  const [bulkBusy, setBulkBusy] = useState(false);
  const [exportBusy, setExportBusy] = useState(false);

  const debouncedQuery = useDebounce(query);
  const debouncedIndustry = useDebounce(industry);
  const debouncedLocation = useDebounce(location);

  const filters: LeadFilters = useMemo(
    () => ({
      q: debouncedQuery || undefined,
      status: status || undefined,
      industry: debouncedIndustry || undefined,
      location: debouncedLocation || undefined,
      score_min: scoreMin ? Number(scoreMin) : undefined,
      score_max: scoreMax ? Number(scoreMax) : undefined,
      sort,
      order: "desc",
      page,
      page_size: 20,
    }),
    [
      debouncedQuery,
      status,
      debouncedIndustry,
      debouncedLocation,
      scoreMin,
      scoreMax,
      sort,
      page,
    ],
  );

  const { data, loading, error, reload } = useLeads(filters);
  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  function resetFilters() {
    setQuery("");
    setStatus("");
    setIndustry("");
    setLocation("");
    setScoreMin("");
    setScoreMax("");
    setSort("created_at");
    setPage(1);
  }

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
      prev.size === items.length && items.length > 0
        ? new Set()
        : new Set(items.map((lead) => lead.id)),
    );
  }

  async function runBulk(agentType: AgentType) {
    if (selected.size === 0 || bulkBusy) return;
    setBulkBusy(true);
    setBanner(null);
    try {
      const run = await queueRun(agentType, {
        lead_ids: Array.from(selected),
        icp: {
          industry: industry.trim() || undefined,
          location: location.trim() || undefined,
          keywords: query.trim() ? [query.trim()] : undefined,
        },
      });
      setBanner({
        kind: "success",
        text: `${agentType} run queued (${run.run_id}). Track it on the Agents page.`,
      });
      setSelected(new Set());
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setBulkBusy(false);
    }
  }

  async function handleExport() {
    if (exportBusy) return;
    setExportBusy(true);
    setBanner(null);
    try {
      const blob = await exportLeads(filters);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `leads-${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setBanner({ kind: "success", text: "Leads exported to CSV." });
    } catch (err) {
      setBanner({ kind: "error", text: getErrorMessage(err) });
    } finally {
      setExportBusy(false);
    }
  }

  const allSelected = items.length > 0 && selected.size === items.length;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-56 flex-1">
          <Input
            label="Search"
            placeholder="Company, contact, domain…"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setPage(1);
            }}
          />
        </div>
        <Select
          label="Status"
          value={status}
          onChange={(event) => {
            setStatus(event.target.value as LeadStatus | "");
            setPage(1);
          }}
          placeholder="All statuses"
          options={LEAD_STATUSES.map((value) => ({
            value,
            label: LEAD_STATUS_META[value].label,
          }))}
          className="w-44"
        />
        <Input
          label="Industry"
          value={industry}
          onChange={(event) => {
            setIndustry(event.target.value);
            setPage(1);
          }}
          className="w-40"
        />
        <Input
          label="Location"
          value={location}
          onChange={(event) => {
            setLocation(event.target.value);
            setPage(1);
          }}
          className="w-40"
        />
        <Input
          label="Min score"
          type="number"
          min={0}
          max={100}
          value={scoreMin}
          onChange={(event) => {
            setScoreMin(event.target.value);
            setPage(1);
          }}
          className="w-28"
        />
        <Input
          label="Max score"
          type="number"
          min={0}
          max={100}
          value={scoreMax}
          onChange={(event) => {
            setScoreMax(event.target.value);
            setPage(1);
          }}
          className="w-28"
        />
        <Select
          label="Sort"
          value={sort}
          onChange={(event) => {
            setSort(event.target.value);
            setPage(1);
          }}
          options={SORT_OPTIONS}
          className="w-44"
        />
        <Button variant="ghost" size="sm" onClick={resetFilters}>
          Reset
        </Button>
        <div className="ml-auto flex gap-2">
          <Dropdown
            label="Run agent on selected"
            items={BULK_AGENTS.map((agent) => ({
              label: agent.label,
              onSelect: () => void runBulk(agent.id),
            }))}
          />
          <Button variant="secondary" loading={exportBusy} onClick={() => void handleExport()}>
            Export CSV
          </Button>
          <Button onClick={() => setFormOpen(true)}>New lead</Button>
        </div>
      </div>

      {selected.size > 0 ? (
        <p className="rounded-md bg-primary/10 px-3 py-2 text-sm text-primary">
          {selected.size} lead{selected.size === 1 ? "" : "s"} selected. Industry, Location and
          Search filters are used as the ICP when you run an agent.
        </p>
      ) : null}

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
          <div className="flex flex-col gap-3" aria-busy="true" aria-label="Loading leads">
            {Array.from({ length: 6 }, (_, index) => (
              <Skeleton key={index} className="h-12" />
            ))}
          </div>
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : items.length === 0 ? (
          <EmptyState
            title="No leads match your filters"
            description="Adjust the filters, or create your first lead."
            action={<Button onClick={() => setFormOpen(true)}>New lead</Button>}
          />
        ) : (
          <>
            <Table>
              <thead>
                <tr>
                  <Th className="w-10">
                    <Checkbox
                      label=""
                      aria-label="Select all leads on this page"
                      checked={allSelected}
                      onChange={toggleSelectAll}
                    />
                  </Th>
                  <Th>Company</Th>
                  <Th>Status</Th>
                  <Th>Score</Th>
                  <Th>Industry</Th>
                  <Th>Location</Th>
                  <Th>Updated</Th>
                </tr>
              </thead>
              <tbody>
                {items.map((lead: Lead) => {
                  const statusMeta = LEAD_STATUS_META[lead.status];
                  const qualification = QUALIFICATION_META[lead.qualification];
                  return (
                    <tr key={lead.id} className="hover:bg-muted-background/60">
                      <Td>
                        <Checkbox
                          label=""
                          aria-label={`Select ${lead.company_name}`}
                          checked={selected.has(lead.id)}
                          onChange={() => toggleSelected(lead.id)}
                        />
                      </Td>
                      <Td>
                        <Link
                          href={`/dashboard/leads/${lead.id}`}
                          className="font-medium text-foreground hover:text-primary hover:underline"
                        >
                          {lead.company_name}
                        </Link>
                        {lead.contact_name ? (
                          <p className="text-xs text-muted">{lead.contact_name}</p>
                        ) : null}
                      </Td>
                      <Td>
                        <Badge tone={statusMeta.tone}>{statusMeta.label}</Badge>
                      </Td>
                      <Td>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{lead.lead_score ?? "—"}</span>
                          <Badge tone={qualification.tone}>{qualification.label}</Badge>
                        </div>
                      </Td>
                      <Td className="text-muted">{lead.industry ?? "—"}</Td>
                      <Td className="text-muted">{lead.location ?? "—"}</Td>
                      <Td className="text-muted">
                        {new Date(lead.updated_at).toLocaleDateString()}
                      </Td>
                    </tr>
                  );
                })}
              </tbody>
            </Table>
            <Pagination page={page} pageSize={20} total={total} onPageChange={setPage} />
          </>
        )}
      </Card>

      {formOpen ? (
        <LeadForm
          open
          onClose={() => setFormOpen(false)}
          onSaved={() => {
            setFormOpen(false);
            reload();
            router.refresh();
          }}
        />
      ) : null}
      {bulkBusy ? (
        <p role="status" className="sr-only">
          Queueing agent run
        </p>
      ) : null}
    </div>
  );
}
