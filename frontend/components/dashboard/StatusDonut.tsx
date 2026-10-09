"use client";

import { Card } from "@/components/ui/Card";
import type { DonutBucket } from "@/lib/dashboardData";

interface StatusDonutProps {
  total: number;
  buckets: DonutBucket[];
}

const SIZE = 220;
const R = 90;
const STROKE = 26;

export function StatusDonut({ total, buckets }: StatusDonutProps) {
  const segments = buckets.reduce(
    (acc, bucket) => {
      const fraction = total === 0 ? 0 : bucket.value / total;
      const length = fraction * 2 * Math.PI * R;
      const dash = `${length} ${2 * Math.PI * R - length}`;
      const offsetValue = acc.offset;
      acc.offset += fraction;
      acc.segments.push({
        ...bucket,
        style: {
          stroke: bucket.color,
          strokeDasharray: dash,
          strokeDashoffset: `${-offsetValue * 2 * Math.PI * R}`,
        },
        fraction,
      });
      return acc;
    },
    { offset: 0, segments: [] as Array<DonutBucket & { style: React.CSSProperties; fraction: number }> },
  ).segments;

  return (
    <Card title="Lead Status Distribution">
      {total === 0 ? (
        <p className="text-sm text-muted">No leads to visualize yet.</p>
      ) : (
        <div className="flex flex-col items-center gap-6 lg:flex-row">
          <svg
            viewBox={`0 0 ${SIZE} ${SIZE}`}
            className="h-56 w-56"
            role="img"
            aria-label="Lead status distribution donut chart"
          >
            <circle cx={SIZE / 2} cy={SIZE / 2} r={R} fill="none" stroke="#f2f5fa" strokeWidth={STROKE} />
            {segments.map((segment, index) => (
              <circle
                key={segment.label + index}
                cx={SIZE / 2}
                cy={SIZE / 2}
                r={R}
                fill="none"
                strokeWidth={STROKE}
                strokeLinecap="round"
                transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
                style={segment.style}
              />
            ))}
            <text x="50%" y="44%" textAnchor="middle" className="fill-foreground text-3xl font-semibold">
              {total}
            </text>
            <text x="50%" y="58%" textAnchor="middle" className="fill-muted text-xs">
              Total Leads
            </text>
          </svg>
          <div className="flex-1 space-y-2.5">
            {buckets.map((bucket) => (
              <div key={bucket.label} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2.5">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ background: bucket.color }} />
                  <span className="text-foreground">{bucket.label}</span>
                </div>
                <span className="font-medium text-foreground">{bucket.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
