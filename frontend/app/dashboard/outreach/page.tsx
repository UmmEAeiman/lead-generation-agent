import { OutreachView } from "@/components/outreach/OutreachView";

export const metadata = { title: "Outreach · AI Lead Generation Agent" };

export default function OutreachPage() {
  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-xl font-semibold text-foreground">Outreach</h1>
        <p className="mt-1 text-sm text-muted">
          Approve and send messages — every send is human-approved.
        </p>
      </header>
      <OutreachView />
    </div>
  );
}
