"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { getErrorMessage } from "@/lib/api/client";
import { register } from "@/lib/api/auth";
import { emailRule, minLength, required, runRules } from "@/lib/validators";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{
    fullName?: string;
    email?: string;
    password?: string;
  }>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;

    const emailError = runRules(email, [required("Email"), emailRule]);
    const passwordError = runRules(password, [
      required("Password"),
      minLength("Password", 8),
    ]);
    setErrors({
      email: emailError ?? undefined,
      password: passwordError ?? undefined,
    });
    if (emailError || passwordError) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      await register({
        email: email.trim(),
        password,
        full_name: fullName.trim() || null,
      });
      router.push("/login?registered=1");
      router.refresh();
    } catch (error) {
      setSubmitError(getErrorMessage(error, "Registration failed."));
      setSubmitting(false);
    }
  }

  return (
    <Card title="Create your account">
      <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
        {submitError ? (
          <p role="alert" className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger">
            {submitError}
          </p>
        ) : null}
        <Input
          label="Full name"
          autoComplete="name"
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
          error={errors.fullName}
          placeholder="Jane Doe (optional)"
        />
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          error={errors.email}
          placeholder="you@company.com"
        />
        <Input
          label="Password"
          type="password"
          autoComplete="new-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          error={errors.password}
          placeholder="At least 8 characters"
        />
        <Button type="submit" loading={submitting} className="w-full">
          Create account
        </Button>
        <p className="text-center text-sm text-muted">
          Already registered?{" "}
          <Link href="/login" className="font-medium text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </Card>
  );
}
