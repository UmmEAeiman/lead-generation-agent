"""Prompt for the Discovery Agent (candidate scoring/filtering support)."""

from typing import Any

ROLE = """You are a discovery agent in a B2B lead-generation system.
You receive candidate companies found by a search provider and an ideal
customer profile (ICP).

Rules:
- Keep only candidates that genuinely match the ICP.
- Never invent companies, contacts, or data — you only filter and rank what you
  were given.
- If nothing matches, return an empty list.
- Failure behavior: when candidates lack information, rank by available signal
  and mark confidence "unknown".
"""

OUTPUT_SCHEMA: dict[str, Any] = {
    "selected_indices": ["integer"],
    "notes": "string",
}


def build_user_prompt(icp: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    icp_lines = "\n".join(f"- {key}: {value}" for key, value in icp.items())
    candidate_lines = "\n".join(
        f"{index}: {c.get('company_name')} | {c.get('website')} | "
        f"{c.get('industry')} | {c.get('location')} | {c.get('contact_name')}"
        for index, c in enumerate(candidates)
    )
    return (
        "Select the candidates that match this ICP.\n\nICP:\n"
        f"{icp_lines}\n\nCANDIDATES:\n{candidate_lines}"
    )
