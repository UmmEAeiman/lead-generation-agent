import { cn } from "@/lib/cn";
import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  title?: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  children?: ReactNode;
}

export function Card({
  title,
  description,
  actions,
  children,
  className,
  ...rest
}: CardProps) {
  return (
    <section
      className={cn(
        "rounded-2xl border border-border bg-surface shadow-[0_1px_3px_rgba(22,39,74,0.05)]",
        className,
      )}
      {...rest}
    >
      {(title || actions) && (
        <header className="flex flex-wrap items-center justify-between gap-2 px-4 pt-4 pb-1 sm:px-6 sm:pt-5">
          <div>
            {title ? (
              <h2 className="text-sm font-semibold text-foreground sm:text-base">{title}</h2>
            ) : null}
            {description ? (
              <p className="mt-0.5 text-xs text-muted sm:text-sm">{description}</p>
            ) : null}
          </div>
          {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
        </header>
      )}
      <div className="px-4 py-3 sm:px-6 sm:py-4">{children}</div>
    </section>
  );
}
