"use client";

import { cn } from "@/lib/cn";
import { useId } from "react";

import type { InputHTMLAttributes } from "react";

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label: string;
}

export function Checkbox({ label, id, className, ...rest }: CheckboxProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;

  return (
    <div className="flex items-center gap-2">
      <input
        id={inputId}
        type="checkbox"
        className={cn(
          "h-4 w-4 rounded border-border text-primary accent-primary",
          className,
        )}
        {...rest}
      />
      <label htmlFor={inputId} className="text-sm text-foreground">
        {label}
      </label>
    </div>
  );
}
