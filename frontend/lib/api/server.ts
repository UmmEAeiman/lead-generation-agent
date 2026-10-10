import { cache } from "react";
import { headers } from "next/headers";

import { ApiRequestError } from "@/lib/api/client";
import type { ApiErrorBody } from "@/types/api";

// Server-side fetches run in Node and need an absolute backend URL.
// Set API_INTERNAL_URL (server-only) in production, e.g. the Render service URL.
const SERVER_API_BASE =
  process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

export const serverApiRequest = cache(
  async function serverApiRequest<T>(path: string): Promise<T> {
    const headerStore = await headers();
    const cookie = headerStore.get("cookie") ?? "";

    let response: Response;
    try {
      response = await fetch(`${SERVER_API_BASE}${path}`, {
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
