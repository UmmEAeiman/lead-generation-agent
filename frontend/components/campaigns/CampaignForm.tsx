"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Textarea } from "@/components/ui/Textarea";
import { getErrorMessage } from "@/lib/api/client";
import { createCampaign, updateCampaign } from "@/lib/api/campaigns";
import { required, runRules } from "@/lib/validators";
import type { Campaign, CampaignCreate } from "@/types/campaign";

interface CampaignFormProps {
  open: boolean;
  campaign?: Campaign | null;
  onClose: () => void;
  onSaved: () => void;
}

export function CampaignForm({ open, campaign, onClose, onSaved }: CampaignFormProps) {
  const editing = Boolean(campaign);
  const [name, setName] = useState(campaign?.name ?? "");
  const [description, setDescription] = useState(campaign?.description ?? "");
  const [industry, setIndustry] = useState(campaign?.target_industry ?? "");
  const [location, setLocation] = useState(campaign?.target_location ?? "");
  const [companySize, setCompanySize] = useState(campaign?.target_company_size ?? "");
  const [keywords, setKeywords] = useState((campaign?.keywords ?? []).join(", "));
  const [nameError, setNameError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;

    const error = runRules(name, [required("Campaign name")]);
    setNameError(error);
    if (error) return;

    const payload: CampaignCreate = {
      name: name.trim(),
      description: description.trim() || null,
      target_industry: industry.trim() || null,
      target_location: location.trim() || null,
      target_company_size: companySize.trim() || null,
      keywords: keywords
        .split(",")
        .map((word) => word.trim())
        .filter(Boolean),
    };

    setSubmitting(true);
    setSubmitError(null);
    try {
      if (editing && campaign) {
        await updateCampaign(campaign.id, payload);
      } else {
        await createCampaign(payload);
      }
      setSubmitting(false);
      onSaved();
    } catch (err) {
      setSubmitError(getErrorMessage(err, "Could not save the campaign."));
      setSubmitting(false);
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      wide
      title={editing ? `Edit ${campaign?.name}` : "New campaign"}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" form="campaign-form" loading={submitting}>
            {editing ? "Save changes" : "Create campaign"}
          </Button>
        </>
      }
    >
      <form id="campaign-form" onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
        {submitError ? (
          <p role="alert" className="rounded-md bg-danger/10 px-3 py-2 text-sm text-danger">
            {submitError}
          </p>
        ) : null}
        <Input
          label="Campaign name"
          required
          value={name}
          onChange={(event) => setName(event.target.value)}
          error={nameError}
          placeholder="Q4 SaaS founders outreach"
        />
        <Textarea
          label="Description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="What is this campaign about?"
        />
        <div className="grid gap-4 sm:grid-cols-3">
          <Input
            label="Target industry"
            value={industry}
            onChange={(event) => setIndustry(event.target.value)}
            placeholder="SaaS"
          />
          <Input
            label="Target location"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            placeholder="United States"
          />
          <Input
            label="Target company size"
            value={companySize}
            onChange={(event) => setCompanySize(event.target.value)}
            placeholder="11-50"
          />
        </div>
        <Input
          label="Keywords"
          value={keywords}
          onChange={(event) => setKeywords(event.target.value)}
          placeholder="funding, hiring, Series A (comma-separated)"
        />
      </form>
    </Modal>
  );
}
