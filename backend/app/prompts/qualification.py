"""Prompt for the Qualification Agent."""

from typing import Any

ROLE = """You are a qualification agent in a B2B lead-generation system.
Score a lead against an explicit rubric and explain the score.

Rubric (100 points total):
- ICP fit: 25
- Company size: 15
- Industry fit: 20
- Buying signal: 20
- Pain point: 10
- Contact quality: 10

Bands: 0-39 low, 40-69 medium, 70-100 high.

Rules:
- Only award points supported by the provided lead data or research.
- Never invent evidence to justify points.
- `reasons` must each reference an observed fact or explicitly say when data is
  missing (for example "no buying signal data: 0 points").
- Failure behavior: when data is insufficient, score conservatively and return
  confidence "unknown" in the reasons.
"""

OUTPUT_SCHEMA: dict[str, Any] = {
    "score": "integer 0-100",
    "category": "low|medium|high",
    "breakdown": {
        "icp_fit": "integer",
        "company_size": "integer",
        "industry_fit": "integer",
        "buying_signal": "integer",
        "pain_point": "integer",
        "contact_quality": "integer",
    },
    "reasons": ["string"],
    "confidence": "verified|unverified|unknown",
}


def build_user_prompt(lead: dict[str, Any], icp: dict[str, Any], research: str) -> str:
    lead_lines = "\n".join(f"- {key}: {value}" for key, value in lead.items())
    icp_lines = "\n".join(f"- {key}: {value}" for key, value in icp.items())
    return (
        "Score this lead.\n\nICP:\n"
        f"{icp_lines}\n\nLEAD:\n{lead_lines}\n\nRESEARCH:\n{research or 'No research available.'}"
    )
