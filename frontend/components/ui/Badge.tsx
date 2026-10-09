import { cn } from "@/lib/cn";
import type { HTMLAttributes } from "react";

export type BadgeTone =
  | "neutral"
  | "info"
  | "primary"
  | "violet"
  | "cyan"
  | "success"
  | "warning"
  | "danger";

const toneClasses: Record<BadgeTone, string> = {
  neutral: "bg-muted-background text-muted",
  info: "bg-info/10 text-info",
  primary: "bg-primary/10 text-primary",
  violet: "bg-violet/10 text-violet",
  cyan: "bg-cyan/10 text-cyan",
  success: "bg-success/10 text-success",
  warning: "bg-warning/10 text-warning",
  danger: "bg-danger/10 text-danger",
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
}

export function Badge({ tone = "neutral", className, ...rest }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium whitespace-nowrap",
        toneClasses[tone],
        className,
      )}
      {...rest}
    />
  );
}
