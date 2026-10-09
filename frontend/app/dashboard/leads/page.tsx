import { LeadsView } from "@/components/leads/LeadsView";

export const metadata = { title: "Leads · AI Lead Generation Agent" };

export default async function LeadsPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const params = await searchParams;
  const initialQuery = typeof params.q === "string" ? params.q : "";

  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-xl font-semibold text-foreground">Leads</h1>
        <p className="mt-1 text-sm text-muted">
          Search, filter, and manage every lead in your workspace.
        </p>
      </header>
      <LeadsView key={initialQuery} initialQuery={initialQuery} />
    </div>
  );
}
