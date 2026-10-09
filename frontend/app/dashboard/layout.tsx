import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { serverApiRequest } from "@/lib/api/server";
import { ApiRequestError } from "@/lib/api/client";
import type { User } from "@/types/auth";

async function fetchCurrentUser(): Promise<User> {
  try {
    return await serverApiRequest<User>("/api/v1/users/me");
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 401) {
      redirect("/login");
    }
    throw error;
  }
}

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const user = await fetchCurrentUser();
  return <AppShell user={user}>{children}</AppShell>;
}
