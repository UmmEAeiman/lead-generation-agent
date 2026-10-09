import { Activity } from "@/components/dashboard/Activity";
import { AgentStatus } from "@/components/dashboard/AgentStatus";
import { CtaCard } from "@/components/dashboard/CtaCard";
import { DateTimePill } from "@/components/dashboard/DateTimePill";
import { PerformanceChart } from "@/components/dashboard/PerformanceChart";
import { RecentLeads } from "@/components/dashboard/RecentLeads";
import { StatCard } from "@/components/dashboard/StatCard";
import { StatusDonut } from "@/components/dashboard/StatusDonut";
import { getDashboardData } from "@/lib/dashboardData";

export async function DashboardOverview() {
  const data = await getDashboardData();

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground sm:text-3xl">
            {data.greeting}, {data.greetingName}!
          </h1>
          <p className="mt-1.5 max-w-2xl text-sm text-muted">
            Your AI lead generation agent is working. Here’s what’s happening today.
          </p>
        </div>
        <DateTimePill initialDate={data.clock.date} initialTime={data.clock.time} />
      </header>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {data.stats.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-border bg-surface shadow-[0_1px_3px_rgba(22,39,74,0.05)]">
              <div className="flex items-center justify-between px-5 pt-5 pb-2">
                <h2 className="text-sm font-semibold text-foreground">Lead Generation Performance</h2>
                <div className="flex items-center gap-1.5 text-xs text-muted">
                  <span className="rounded-lg bg-muted-background px-2 py-1">7D</span>
                  <span className="rounded-lg px-2 py-1 hover:bg-muted-background">30D</span>
                  <span className="rounded-lg px-2 py-1 hover:bg-muted-background">90D</span>
                </div>
              </div>
              <div className="px-4 pb-4 sm:px-5 sm:pb-5">
                <PerformanceChart chartLeads={data.chartLeads} truncated={data.chartTruncated} />
              </div>
            </div>
            <StatusDonut total={data.donutTotal} buckets={data.buckets} />
          </div>
          <RecentLeads leads={data.recentLeads} />
        </div>
        <div className="space-y-6">
          <CtaCard />
          <AgentStatus items={data.agentItems} anyRunning={data.anyRunning} />
          <Activity activity={data.activity} />
        </div>
      </div>
    </div>
  );
}
