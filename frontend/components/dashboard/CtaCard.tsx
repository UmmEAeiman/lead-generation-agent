import Link from "next/link";
import { Button } from "@/components/ui/Button";

export function CtaCard() {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#7d93fb] to-[#6194fd] p-5 text-white shadow-[0_4px_14px_rgba(97,148,253,0.3)] sm:p-6">
      <div className="relative z-10 flex flex-col gap-4">
        <div>
          <p className="text-sm font-semibold leading-snug">
            Let AI find, qualify and reach out to your ideal customers automatically.
          </p>
          <p className="mt-1 text-xs text-white/85">
            Run the Lead Generation Agent to fill your pipeline faster.
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs font-medium text-white/90">Start New Campaign</p>
          <Link href="/dashboard/agents">
            <Button
              variant="secondary"
              size="sm"
              className="!bg-white/95 !text-foreground hover:!bg-white"
            >
              Run Lead Generation Agent
            </Button>
          </Link>
        </div>
      </div>
      <div
        aria-hidden="true"
        className="absolute -right-24 -top-24 h-56 w-56 rounded-full bg-white/10 blur-3xl"
      />
    </div>
  );
}
