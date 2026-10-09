"""Prompt for the Enrichment Agent."""

from typing import Any

ROLE = """You are an enrichment agent in a B2B lead-generation system.
Your job is to fill in missing fields for a company lead.

Rules:
- Only state values you can support from the provided context.
- Mark every field in field_confidence as "verified" (explicitly supported by
  context), "unverified" (plausible but unsupported), or "unknown".
- NEVER fabricate emails, phone numbers, names, roles, URLs, or company facts.
- If a value is unknown, return null for the field and "unknown" for its confidence.
- Failure behavior: if the context is insufficient, return the original values
  unchanged with confidence "unknown" for anything you cannot support.
"""

OUTPUT_SCHEMA: dict[str, Any] = {
    "company_name": "string",
    "website": "string|null",
    "industry": "string|null",
    "location": "string|null",
    "company_size": "string|null",
    "contact_name": "string|null",
    "contact_role": "string|null",
    "email": "string|null",
    "description": "string|null",
    "field_confidence": {"<field>": "verified|unverified|unknown"},
}


def build_user_prompt(lead: dict[str, Any], context: str) -> str:
    lead_lines = "\n".join(f"- {key}: {value}" for key, value in lead.items())
    context_text = context or "No additional context provided."
    return (
        "Enrich this lead. Only use the context below; mark anything the "
        f"context does not support as unknown.\n\nLEAD:\n{lead_lines}\n\n"
        f"CONTEXT:\n{context_text}"
    )
