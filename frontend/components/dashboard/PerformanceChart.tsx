"use client";

import { useMemo } from "react";

interface PerformanceChartProps {
  chartLeads: Array<{ created_at: string; status: string }>;
  truncated: boolean;
}

const COLORS = {
  qualified: "#35d49d",
  contacted: "#7636f1",
  outreach: "#1e67fd",
  meeting: "#ff971b",
  total: "#cbd5f5",
};

export function PerformanceChart({ chartLeads, truncated }: PerformanceChartProps) {
  const points = useMemo(() => {
    const now = new Date();
    const days = 7;
    const series = Array.from({ length: days }).map((_, index) => {
      const base = new Date(now);
      base.setDate(base.getDate() - (days - 1 - index));
      base.setHours(0, 0, 0, 0);
      const end = new Date(base);
      end.setHours(23, 59, 59, 999);
      const startTime = base.getTime();
      const endTime = end.getTime();
      const inDay = chartLeads.filter((lead) => {
        const ts = new Date(lead.created_at).getTime();
        return ts >= startTime && ts <= endTime;
      });
      return {
        label: base.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        total: inDay.length,
        qualified: inDay.filter((lead) => lead.status === "QUALIFIED" || lead.status === "INTERESTED" || lead.status === "MEETING_BOOKED" || lead.status === "CONVERTED").length,
        contacted: inDay.filter((lead) => lead.status === "CONTACTED" || lead.status === "REPLIED").length,
      };
    });
    const max = Math.max(1, ...series.map((s) => s.total));
    return series.map((s, index) => {
      const x = index * 160 + 40;
      const y = (total: number) => 140 - (total / max) * 90;
      return {
        ...s,
        x,
        yTotal: y(s.total),
        yQualified: y(s.qualified),
        yContacted: y(s.contacted),
      };
    });
  }, [chartLeads]);

  if (chartLeads.length === 0) {
    return (
      <p className="text-sm text-muted">Not enough data to plot performance yet.</p>
    );
  }

  const width = 7 * 160 + 40;
  const height = 180;

  return (
    <div className="space-y-3">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="h-[200px] w-full"
        role="img"
        aria-label="Lead generation performance chart"
      >
        <line x1="40" y1="140" x2={width - 40} y2="140" stroke="#e8edf4" strokeWidth="1" />
        {[0, 1, 2, 3].map((i) => (
          <line
            key={i}
            x1="40"
            y1={140 - i * 22.5}
            x2={width - 40}
            y2={140 - i * 22.5}
            stroke="#f2f5fa"
            strokeWidth="1"
          />
        ))}
        {points.map((point, index) => {
          const next = points[index + 1];
          if (!next) return null;
          return (
            <g key={point.label}>
              <line
                x1={point.x}
                y1={point.yTotal}
                x2={next.x}
                y2={next.yTotal}
                stroke={COLORS.total}
                strokeWidth="2"
                strokeDasharray="4 4"
              />
              <line
                x1={point.x}
                y1={point.yQualified}
                x2={next.x}
                y2={next.yQualified}
                stroke={COLORS.qualified}
                strokeWidth="2"
              />
              <line
                x1={point.x}
                y1={point.yContacted}
                x2={next.x}
                y2={next.yContacted}
                stroke={COLORS.contacted}
                strokeWidth="2"
                opacity="0.8"
              />
            </g>
          );
        })}
        {points.map((point) => (
          <g key={`dot-${point.label}`}>
            <circle cx={point.x} cy={point.yTotal} r="4" fill={COLORS.total} />
            <circle cx={point.x} cy={point.yQualified} r="4" fill={COLORS.qualified} />
            <circle cx={point.x} cy={point.yContacted} r="4" fill={COLORS.contacted} />
            <text x={point.x} y="160" textAnchor="middle" className="fill-muted text-[11px]">
              {point.label}
            </text>
          </g>
        ))}
      </svg>
      <div className="flex flex-wrap items-center gap-3 text-xs text-muted">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-[color:var(--primary)]" />
          Meetings/Qualified trend
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-[#35d49d]" />
          Qualified
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-[#7636f1]" />
          Contacted
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-[#cbd5f5]" />
          Total Leads
        </span>
      </div>
      {truncated ? <p className="text-xs text-muted">Showing last {chartLeads.length} leads.</p> : null}
    </div>
  );
}
