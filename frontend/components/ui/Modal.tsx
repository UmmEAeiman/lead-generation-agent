"use client";

import { useEffect } from "react";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/Button";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  wide?: boolean;
}

export function Modal({ open, onClose, title, children, footer, wide }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-foreground/40 p-4 sm:items-center"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={`flex max-h-[90vh] w-full flex-col rounded-lg bg-surface shadow-xl ${
          wide ? "max-w-2xl" : "max-w-md"
        }`}
      >
        <header className="flex items-center justify-between border-b border-border px-4 py-3 sm:px-6">
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close dialog">
            ✕
          </Button>
        </header>
        <div className="overflow-y-auto px-4 py-4 sm:px-6">{children}</div>
        {footer ? (
          <footer className="flex justify-end gap-2 border-t border-border px-4 py-3 sm:px-6">
            {footer}
          </footer>
        ) : null}
      </div>
    </div>
  );
}
