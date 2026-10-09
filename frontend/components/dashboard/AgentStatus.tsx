import { Card } from "@/components/ui/Card";
import type { AgentStatusItem } from "@/lib/dashboardData";

interface AgentStatusProps {
  items: AgentStatusItem[];
  anyRunning: boolean;
}

export function AgentStatus({ items, anyRunning }: AgentStatusProps) {
  return (
    <Card title="Agent Status" actions={anyRunning ? <span className="text-xs text-success">● Running</span> : null}>
      {items.length === 0 ? (
        <p className="text-sm text-muted">No agent runs yet. Queue a run from the Agents page.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-border/70">
          {items.map((item) => (
            <li key={item.id} className="flex items-center justify-between gap-3 py-2.5 text-sm">
              <span className="font-medium text-foreground">{item.label}</span>
              <span
                className={
                  item.tone === "success"
                    ? "text-xs text-success"
                    : item.tone === "danger"
                      ? "text-xs text-danger"
                      : "text-xs text-muted"
                }
              >
                {item.statusText}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
