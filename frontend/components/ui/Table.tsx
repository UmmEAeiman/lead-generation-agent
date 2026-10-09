import { cn } from "@/lib/cn";
import type { ReactNode } from "react";

interface TableProps {
  children: ReactNode;
  className?: string;
}

export function Table({ children, className }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className={cn("w-full border-collapse text-sm", className)}>
        {children}
      </table>
    </div>
  );
}

interface CellProps {
  children?: ReactNode;
  className?: string;
}

export function Th({ children, className }: CellProps) {
  return (
    <th
      scope="col"
      className={cn(
        "border-b border-border/70 px-3 py-2 text-left text-xs font-medium text-muted",
        className,
      )}
    >
      {children}
    </th>
  );
}

export function Td({ children, className }: CellProps) {
  return (
    <td className={cn("border-b border-border/70 px-3 py-2.5 text-foreground", className)}>
      {children}
    </td>
  );
}
