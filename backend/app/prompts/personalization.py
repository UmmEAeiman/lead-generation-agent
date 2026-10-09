"""Prompt for the Personalization Agent."""

from typing import Any

ROLE = """You are a personalization agent in a B2B lead-generation system.
Write a short, personalized outreach message using ONLY verified research.

Strict rules — never invent:
- personal achievements, company facts, job titles, customer relationships,
  events, revenue, or technology usage.
- If information is unknown, OMIT it. Do not hedge with guesses.
- Mention at most two research-backed details.
- Tone: professional, direct, no hype, no placeholders like [Name].
- Failure behavior: if there is no verified research, return a neutral message
  that only references the lead's industry and a general business outcome.
- Message length: 60-110 words.
"""

OUTPUT_SCHEMA: dict[str, Any] = {
    "subject": "string",
    "message": "string",
    "used_facts": ["string"],
    "omitted_info": ["string"],
}


def build_user_prompt(lead: dict[str, Any], research_summary: str, pain_points: list[str]) -> str:
    lead_lines = "\n".join(f"- {key}: {value}" for key, value in lead.items())
    pains = "\n".join(f"- {p}" for p in pain_points) or "- none identified"
    return (
        "Write the outreach message.\n\nLEAD:\n"
        f"{lead_lines}\n\nRESEARCH SUMMARY:\n{research_summary or 'None'}\n\n"
        f"PAIN POINTS:\n{pains}"
    )
