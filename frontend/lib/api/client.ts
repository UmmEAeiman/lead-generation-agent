import type { ApiErrorBody } from "@/types/api";

// Empty base => same-origin requests, proxied to the backend by the /api/v1 rewrite
// in next.config.ts. Set NEXT_PUBLIC_API_URL to call an absolute backend URL instead.
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export class ApiRequestError extends Error {
  readonly code: string;
  readonly status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.code = code;
    this.status = status;
  }
}

export function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const isFormData = options.body instanceof FormData;
  const headers = new Headers(options.headers);
  if (options.body && !isFormData) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      ...options,
      headers,
      credentials: "include",
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

  const text = await response.text();
  let payload: unknown = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = null;
    }
  }

  if (!response.ok) {
    const body = payload as ApiErrorBody | null;
    const code = body?.error?.code ?? `HTTP_${response.status}`;
    const message =
      body?.error?.message ??
      (response.status === 401
        ? "Your session has expired. Please sign in again."
        : "Request failed. Please try again.");
    throw new ApiRequestError(code, message, response.status);
  }

  return payload as T;
}

export function getErrorMessage(error: unknown, fallback = "Something went wrong."): string {
  if (error instanceof ApiRequestError) return error.message;
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

export async function apiRequestBlob(
  path: string,
  options: RequestInit = {},
): Promise<Blob> {
  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      ...options,
      credentials: "include",
      cache: "no-store",
    });
  } catch {
    throw new ApiRequestError(
      "NETWORK_ERROR",
      "Could not reach the server. Is the backend running?",
      0,
    );
  }

  if (!response.ok) {
    const text = await response.text();
    let payload: unknown = null;
    if (text) {
      try {
        payload = JSON.parse(text);
      } catch {
        payload = null;
      }
    }
    const body = payload as ApiErrorBody | null;
    const code = body?.error?.code ?? `HTTP_${response.status}`;
    const message =
      body?.error?.message ??
      (response.status === 401
        ? "Your session has expired. Please sign in again."
        : "Request failed. Please try again.");
    throw new ApiRequestError(code, message, response.status);
  }

  return response.blob();
}
