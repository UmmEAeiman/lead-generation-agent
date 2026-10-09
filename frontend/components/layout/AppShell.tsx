"use client";

import { useState } from "react";
import type { ReactNode } from "react";

import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import type { User } from "@/types/auth";

interface AppShellProps {
  user: User;
  children: ReactNode;
}

export function AppShell({ user, children }: AppShellProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-border bg-surface shadow-[0_1px_0_rgba(22,39,74,0.05)] lg:block">
        <Sidebar />
      </aside>

      {mobileNavOpen ? (
        <div
          className="fixed inset-0 z-40 bg-foreground/40 lg:hidden"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setMobileNavOpen(false);
          }}
        >
          <aside className="h-full w-64 border-r border-border bg-surface shadow-xl">
            <Sidebar onNavigate={() => setMobileNavOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="flex min-h-screen flex-col lg:pl-64">
        <Header user={user} onMenuToggle={() => setMobileNavOpen((value) => !value)} />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
