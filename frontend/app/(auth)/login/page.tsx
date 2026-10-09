"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { getErrorMessage } from "@/lib/api/client";
import { login } from "@/lib/api/auth";
import { emailRule, required, runRules } from "@/lib/validators";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;

    const emailError = runRules(email, [required("Email"), emailRule]);
    const passwordError = runRules(password, [required("Password")]);
    setErrors({ email: emailError ?? undefined, password: passwordError ?? undefined });
    if (emailError || passwordError) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      await login({ email: email.trim(), password });
      router.push("/dashboard");
      router.refresh();
    } catch (error) {
      setSubmitError(getErrorMessage(error, "Sign in failed."));
      setSubmitting(false);
    }
  }

  return (
    <Card title="Sign in">
      <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
        {submitError ? (
          <p role="alert" className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger">
            {submitError}
          </p>
        ) : null}
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          error={errors.email}
          placeholder="you@company.com"
        />
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          error={errors.password}
          placeholder="••••••••"
        />
        <Button type="submit" loading={submitting} className="w-full">
          Sign in
        </Button>
        <p className="text-center text-sm text-muted">
          No account?{" "}
          <Link href="/register" className="font-medium text-primary hover:underline">
            Create one
          </Link>
        </p>
      </form>
    </Card>
  );
}
