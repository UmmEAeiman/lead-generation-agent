"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Textarea } from "@/components/ui/Textarea";
import { getErrorMessage } from "@/lib/api/client";
import { createLead, updateLead } from "@/lib/api/leads";
import {
  emailRule,
  optionalUrl,
  required,
  runRules,
} from "@/lib/validators";
import type { Lead, LeadCreate } from "@/types/lead";

type FormState = {
  company_name: string;
  website: string;
  email: string;
  industry: string;
  location: string;
  company_size: string;
  contact_name: string;
  contact_role: string;
  phone: string;
  linkedin_url: string;
  source: string;
  description: string;
};

const EMPTY_FORM: FormState = {
  company_name: "",
  website: "",
  email: "",
  industry: "",
  location: "",
  company_size: "",
  contact_name: "",
  contact_role: "",
  phone: "",
  linkedin_url: "",
  source: "",
  description: "",
};

function toFormState(lead: Lead): FormState {
  return {
    company_name: lead.company_name,
    website: lead.website ?? "",
    email: lead.email ?? "",
    industry: lead.industry ?? "",
    location: lead.location ?? "",
    company_size: lead.company_size ?? "",
    contact_name: lead.contact_name ?? "",
    contact_role: lead.contact_role ?? "",
    phone: lead.phone ?? "",
    linkedin_url: lead.linkedin_url ?? "",
    source: lead.source ?? "",
    description: lead.description ?? "",
  };
}

function nullIfEmpty(value: string): string | null {
  return value.trim() ? value.trim() : null;
}

interface LeadFormProps {
  open: boolean;
  lead?: Lead | null;
  onClose: () => void;
  onSaved: (lead: Lead) => void;
}

export function LeadForm({ open, lead, onClose, onSaved }: LeadFormProps) {
  const editing = Boolean(lead);
  const [form, setForm] = useState<FormState>(() =>
    lead ? toFormState(lead) : EMPTY_FORM,
  );
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function setField(field: keyof FormState, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;

    const companyError = runRules(form.company_name, [required("Company name")]);
    const emailError = form.email ? runRules(form.email, [emailRule]) : null;
    const websiteError = form.website ? runRules(form.website, [optionalUrl]) : null;
    setErrors({
      company_name: companyError ?? undefined,
      email: emailError ?? undefined,
      website: websiteError ?? undefined,
    });
    if (companyError || emailError || websiteError) return;

    const payload: LeadCreate = {
      company_name: form.company_name.trim(),
      website: nullIfEmpty(form.website),
      email: nullIfEmpty(form.email),
      industry: nullIfEmpty(form.industry),
      location: nullIfEmpty(form.location),
      company_size: nullIfEmpty(form.company_size),
      contact_name: nullIfEmpty(form.contact_name),
      contact_role: nullIfEmpty(form.contact_role),
      phone: nullIfEmpty(form.phone),
      linkedin_url: nullIfEmpty(form.linkedin_url),
      source: nullIfEmpty(form.source),
      description: nullIfEmpty(form.description),
    };

    setSubmitting(true);
    setSubmitError(null);
    try {
      const saved = editing && lead
        ? await updateLead(lead.id, payload)
        : await createLead(payload);
      setSubmitting(false);
      onSaved(saved);
      setForm(EMPTY_FORM);
      setErrors({});
    } catch (error) {
      setSubmitError(getErrorMessage(error, "Could not save the lead."));
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      wide
      title={editing ? `Edit ${lead?.company_name}` : "New lead"}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" form="lead-form" loading={submitting}>
            {editing ? "Save changes" : "Create lead"}
          </Button>
        </>
      }
    >
      <form id="lead-form" onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
        {submitError ? (
          <p role="alert" className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger">
            {submitError}
          </p>
        ) : null}
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Company name"
            required
            value={form.company_name}
            onChange={(event) => setField("company_name", event.target.value)}
            error={errors.company_name}
          />
          <Input
            label="Website"
            placeholder="https://example.com"
            value={form.website}
            onChange={(event) => setField("website", event.target.value)}
            error={errors.website}
          />
          <Input
            label="Email"
            type="email"
            value={form.email}
            onChange={(event) => setField("email", event.target.value)}
            error={errors.email}
          />
          <Input
            label="Phone"
            value={form.phone}
            onChange={(event) => setField("phone", event.target.value)}
          />
          <Input
            label="Industry"
            value={form.industry}
            onChange={(event) => setField("industry", event.target.value)}
          />
          <Input
            label="Location"
            value={form.location}
            onChange={(event) => setField("location", event.target.value)}
          />
          <Input
            label="Company size"
            placeholder="e.g. 11-50"
            value={form.company_size}
            onChange={(event) => setField("company_size", event.target.value)}
          />
          <Input
            label="Source"
            placeholder="e.g. website, referral"
            value={form.source}
            onChange={(event) => setField("source", event.target.value)}
          />
          <Input
            label="Contact name"
            value={form.contact_name}
            onChange={(event) => setField("contact_name", event.target.value)}
          />
          <Input
            label="Contact role"
            value={form.contact_role}
            onChange={(event) => setField("contact_role", event.target.value)}
          />
          <Input
            label="LinkedIn URL"
            placeholder="https://linkedin.com/in/…"
            value={form.linkedin_url}
            onChange={(event) => setField("linkedin_url", event.target.value)}
          />
        </div>
        <Textarea
          label="Description"
          value={form.description}
          onChange={(event) => setField("description", event.target.value)}
          placeholder="Anything useful about this lead"
        />
      </form>
    </Modal>
  );
}
