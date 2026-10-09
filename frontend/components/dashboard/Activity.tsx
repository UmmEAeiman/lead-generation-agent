import Link from "next/link";
import { formatRelative } from "@/lib/format";
import { Card } from "@/components/ui/Card";
import type { ActivityItem } from "@/lib/dashboardData";

interface ActivityProps {
  activity: ActivityItem[];
}

export function Activity({ activity }: ActivityProps) {
  return (
    <Card
      title="Recent Activity"
      actions={
        <Link href="/dashboard/leads" className="text-xs font-medium text-primary hover:underline">
          View All
        </Link>
      }
    >
      {activity.length === 0 ? (
        <p className="text-sm text-muted">No recent activity yet.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-border/70">
          {activity.map((item) => (
            <li key={item.id} className="flex flex-col gap-0.5 py-2.5 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-foreground">{item.title}</p>
                <p className="text-xs text-muted">{item.source}</p>
              </div>
              <span className="text-xs text-muted sm:text-right">{formatRelative(item.at)}</span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
