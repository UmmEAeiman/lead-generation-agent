import type { ReactNode } from "react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <p className="text-lg font-semibold text-primary">AI Lead Generation Agent</p>
          <p className="mt-1 text-sm text-muted">
            Find, qualify, and reach the right leads with AI agents.
          </p>
        </div>
        {children}
      </div>
    </main>
  );
}
