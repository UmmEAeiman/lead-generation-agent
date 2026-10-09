interface StatCardProps {
  label: string;
  value: number;
  sub: string;
}

export function StatCard({ label, value, sub }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-4 shadow-[0_1px_3px_rgba(22,39,74,0.05)] sm:p-5">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-1.5 text-2xl font-semibold text-foreground sm:text-3xl">{value}</p>
      <p className="mt-1.5 line-clamp-2 text-xs text-muted">{sub}</p>
    </div>
  );
}
