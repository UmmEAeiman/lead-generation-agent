"use client";

import { useEffect, useState } from "react";

interface DateTimePillProps {
  initialDate: string;
  initialTime: string;
}

export function DateTimePill({ initialDate, initialTime }: DateTimePillProps) {
  const [date, setDate] = useState(initialDate);
  const [time, setTime] = useState(initialTime);

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setDate(
        now.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
          timeZone: "UTC",
        }),
      );
      setTime(
        `${now.toLocaleTimeString("en-US", {
          hour: "numeric",
          minute: "2-digit",
          timeZone: "UTC",
        })} (UTC)`,
      );
    }, 10_000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="shrink-0 rounded-xl border border-border bg-surface px-3.5 py-2 text-right shadow-[0_1px_3px_rgba(22,39,74,0.05)]">
      <p className="text-xs font-semibold text-foreground">{date}</p>
      <p className="text-[11px] text-muted">{time}</p>
    </div>
  );
}
