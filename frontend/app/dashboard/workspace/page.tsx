import { WorkspaceView } from '@/components/workspace/WorkspaceView';

export const metadata = { title: 'Workspace · AI Lead Generation Agent' };

export default async function WorkspacePage({
  searchParams,
}: {
  searchParams: Promise<{ run_id?: string }>;
}) {
  const params = await searchParams;
  const runId = typeof params.run_id === "string" ? params.run_id : "";
  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-xl font-semibold text-foreground">Workspace</h1>
        <p className="mt-1 text-sm text-muted">
          One page to review a finished run&apos;s leads, outreach drafts, and approve/send outreach.
        </p>
      </header>
      <WorkspaceView initialRunId={runId} />
    </div>
  );
}