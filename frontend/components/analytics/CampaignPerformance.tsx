import { serverApiRequest } from "@/lib/api/server";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Table, Td, Th } from "@/components/ui/Table";
import type { AnalyticsOverview, CampaignPerformanceRow } from "@/types/analytics";

function hasRows(rows: CampaignPerformanceRow[]): boolean {
  return rows.length > 0;
}

export async function CampaignPerformance() {
  let rows: CampaignPerformanceRow[] = [];
  try {
    const data = await serverApiRequest<AnalyticsOverview>(
      "/api/v1/analytics/overview",
    );
    rows = data.campaign_performance;
  } catch {
    rows = [];
  }

  return (
    <Card title="Campaign performance" description="Leads, replies, and conversions per campaign">
      {!hasRows(rows) ? (
        <EmptyState
          title="No campaign data yet"
          description="Create a campaign and run discovery to see performance here."
        />
      ) : (
        <Table>
          <thead>
            <tr>
              <Th>Campaign</Th>
              <Th className="text-right">Leads</Th>
              <Th className="text-right">Qualified</Th>
              <Th className="text-right">Contacted</Th>
              <Th className="text-right">Replies</Th>
              <Th className="text-right">Conversions</Th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.campaign_id}>
                <Td className="font-medium">{row.name}</Td>
                <Td className="text-right">{row.total_leads}</Td>
                <Td className="text-right">{row.qualified}</Td>
                <Td className="text-right">{row.contacted}</Td>
                <Td className="text-right">{row.replies}</Td>
                <Td className="text-right">{row.conversions}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Card>
  );
}
