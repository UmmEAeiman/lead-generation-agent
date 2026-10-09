import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Table, Td, Th } from "@/components/ui/Table";
import { LEAD_STATUS_META } from "@/lib/statusMeta";
import type { RecentLeadRow } from "@/lib/dashboardData";

interface RecentLeadsProps {
  leads: RecentLeadRow[];
}

export function RecentLeads({ leads }: RecentLeadsProps) {
  return (
    <Card
      title="Recent Leads"
      actions={
        <Link href="/dashboard/leads" className="text-xs font-medium text-primary hover:underline">
          View All
        </Link>
      }
    >
      {leads.length === 0 ? (
        <p className="text-sm text-muted">No leads yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <thead>
              <tr>
                <Th>Name</Th>
                <Th>Company</Th>
                <Th>Email</Th>
                <Th>Score</Th>
                <Th>Status</Th>
                <Th className="text-right">Added</Th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id}>
                  <Td>
                    <Link
                      href={`/dashboard/leads/${lead.id}`}
                      className="font-medium text-foreground hover:text-primary hover:underline"
                    >
                      {lead.name}
                    </Link>
                  </Td>
                  <Td className="text-muted">{lead.company}</Td>
                  <Td className="truncate text-muted">{lead.email ?? "—"}</Td>
                  <Td>{lead.score ?? "—"}</Td>
                  <Td>
                    <Badge tone={LEAD_STATUS_META[lead.status].tone}>
                      {LEAD_STATUS_META[lead.status].label}
                    </Badge>
                  </Td>
                  <Td className="text-right text-muted">
                    {new Date(lead.createdAt).toLocaleDateString(undefined, {
                      month: "short",
                      day: "numeric",
                    })}
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </Card>
  );
}
