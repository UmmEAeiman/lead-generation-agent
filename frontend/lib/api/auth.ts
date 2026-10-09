import { apiRequest } from "@/lib/api/client";
import type { LoginRequest, RegisterRequest, User } from "@/types/auth";

export function login(data: LoginRequest): Promise<User> {
  return apiRequest<User>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function register(data: RegisterRequest): Promise<User> {
  return apiRequest<User>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function logout(): Promise<void> {
  return apiRequest<void>("/api/v1/auth/logout", { method: "POST" });
}

export function getCurrentUser(): Promise<User> {
  return apiRequest<User>("/api/v1/users/me");
}
