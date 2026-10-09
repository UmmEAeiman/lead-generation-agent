import { LeadDetail } from "@/components/leads/LeadDetail";

export const metadata = { title: "Lead · AI Lead Generation Agent" };

export default async function LeadDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <LeadDetail leadId={id} />;
}
