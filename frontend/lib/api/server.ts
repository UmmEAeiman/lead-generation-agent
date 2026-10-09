import { cache } from "react";
import { headers } from "next/headers";

import { ApiRequestError, apiUrl } from "@/lib/api/client";
import type { ApiErrorBody } from "@/types/api";

export const serverApiRequest = cache(
  async function serverApiRequest<T>(path: string): Promise<T> {
    const headerStore = await headers();
    const cookie = headerStore.get("cookie") ?? "";

    let response: Response;
    try {
      response = await fetch(apiUrl(path), {
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
