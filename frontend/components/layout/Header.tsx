"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { getErrorMessage } from "@/lib/api/client";
import { logout } from "@/lib/api/auth";
import type { User } from "@/types/auth";

interface HeaderProps {
  user: User;
  onMenuToggle: () => void;
}

export function Header({ user, onMenuToggle }: HeaderProps) {
  const router = useRouter();
  const [signingOut, setSigningOut] = useState(false);
  const [search, setSearch] = useState("");

  async function onSignOut() {
    if (signingOut) return;
    setSigningOut(true);
    try {
      await logout();
    } catch (error) {
      // Even if the request fails, drop local navigation state.
      console.warn(getErrorMessage(error));
    }
    router.push("/login");
    router.refresh();
  }

  function onSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = search.trim();
    router.push(query ? `/dashboard/leads?q=${encodeURIComponent(query)}` : "/dashboard/leads");
  }

  const displayName = user.full_name || user.email;
  const initials = displayName
    .split(/[\s@_.-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  return (
    <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-border bg-surface px-4 py-2.5 sm:px-6">
      <button
        type="button"
        onClick={onMenuToggle}
        aria-label="Open navigation menu"
        className="rounded-lg border border-border px-2 py-1.5 text-sm text-foreground hover:bg-muted-background lg:hidden"
      >
        ☰
      </button>

      <form onSubmit={onSearch} role="search" className="min-w-0 flex-1 sm:max-w-md">
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search leads, companies, or people..."
          aria-label="Search leads, companies, or people"
          className="w-full rounded-lg border border-border bg-[#fbfcfe] px-3.5 py-2 text-sm text-foreground placeholder:text-muted focus:border-primary/50 focus:bg-surface focus:outline-none"
        />
      </form>

      <div className="ml-auto flex items-center gap-3">
        <div className="hidden text-right sm:block">
          <p className="max-w-[160px] truncate text-sm font-semibold text-foreground">
            {displayName}
          </p>
          <p className="max-w-[160px] truncate text-xs text-muted">{user.email}</p>
        </div>
        <div
          aria-hidden="true"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#eef2fe] text-xs font-semibold text-primary"
        >
          {initials || "U"}
        </div>
        <Button variant="secondary" size="sm" onClick={onSignOut} loading={signingOut}>
          Sign out
        </Button>
      </div>
    </header>
  );
}
