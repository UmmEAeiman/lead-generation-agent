"use client";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="mx-auto max-w-lg py-16">
      <Card title="Something went wrong">
        <p className="text-sm text-muted">
          {error.message || "An unexpected error occurred while loading this page."}
        </p>
        <div className="mt-4">
          <Button variant="secondary" onClick={reset}>
            Try again
          </Button>
        </div>
      </Card>
    </div>
  );
}
