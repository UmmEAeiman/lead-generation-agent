import { cache } from "react";
import { headers } from "next/headers";

import { ApiRequestError } from "@/lib/api/client";
import type { ApiErrorBody } from "@/types/api";

function normalizeBaseUrl(value: string | undefined): string | null {
  if (!value) {
    return null;
  }
  const trimmed = value.trim().replace(/\/+$/, "");
  return /^https?:\/\//i.test(trimmed) ? trimmed : null;
}

// Optional absolute backend URL for non-Vercel hosts (e.g. Docker/Oracle).
const CONFIGURED_API_BASE =
  normalizeBaseUrl(process.env.API_INTERNAL_URL) ??
  normalizeBaseUrl(process.env.NEXT_PUBLIC_API_URL);

// On Vercel the browser already reaches the backend through the /api/v1 rewrite.
// Reusing that same-origin proxy for server-side fetches removes any dependency
// on API_INTERNAL_URL being configured correctly in the project settings.
async function resolveApiBase(): Promise<string> {
  if (process.env.VERCEL) {
    const headerStore = await headers();
    const host = headerStore.get("x-forwarded-host") ?? headerStore.get("host");
    const proto = headerStore.get("x-forwarded-proto") ?? "https";
    if (host) {
      return `${proto}://${host}`;
    }
  }
  return CONFIGURED_API_BASE ?? "http://localhost:8001";
}

export const serverApiRequest = cache(
  async function serverApiRequest<T>(path: string): Promise<T> {
    const headerStore = await headers();
    const cookie = headerStore.get("cookie") ?? "";
    const base = await resolveApiBase();

    let response: Response;
    try {
      response = await fetch(`${base}${path}`, {
        headers: cookie ? { cookie } : undefined,
        cache: "no-store",
      });
    } catch {
      throw new ApiRequestError(
        "NETWORK_ERROR",
        "Could not reach the server. Is the backend running?",
        0,
      );
    }

    if (response.status === 204) {
      return undefined as T;
    }

    const payload: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      const body = payload as ApiErrorBody | null;
      throw new ApiRequestError(
        body?.error?.code ?? `HTTP_${response.status}`,
        body?.error?.message ?? "Request failed.",
        response.status,
      );
    }
    return payload as T;
  },
);
