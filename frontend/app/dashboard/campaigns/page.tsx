import { CampaignsView } from "@/components/campaigns/CampaignsView";

export const metadata = { title: "Campaigns · AI Lead Generation Agent" };

export default function CampaignsPage() {
  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="text-xl font-semibold text-foreground">Campaigns</h1>
        <p className="mt-1 text-sm text-muted">
          Define ideal customer profiles and run discovery against them.
        </p>
      </header>
      <CampaignsView />
    </div>
  );
}
