import { AgentsView } from "@/components/agents/AgentsView";

export const metadata = { title: "Agents · AI Lead Generation Agent" };

export default function AgentsPage() {
  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-xl font-semibold text-foreground">Agents</h1>
        <p className="mt-1 text-sm text-muted">
          Run background AI agents and watch their progress.
        </p>
      </header>
      <AgentsView />
    </div>
  );
}
