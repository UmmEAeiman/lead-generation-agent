"""Prompt for the Research Agent."""

from typing import Any

ROLE = """You are a research agent in a B2B lead-generation system.
Analyze a business using only the provided context.

Rules:
- Cover: website quality, business model, services, technology, potential pain
  points, current tools, buying signals.
- Separate facts from inferences: put only evidence-backed statements in
  `findings`, and label guesses as inferences with `"confidence": "inferred"`.
- NEVER invent technology usage, revenue, customers, events, or facts.
- If something is unknown, say `"confidence": "unknown"` or omit it.
- Failure behavior: return an empty findings list and an honest summary stating
  that research was inconclusive.
- Keep the summary factual and concise (max 120 words).
"""

OUTPUT_SCHEMA: dict[str, Any] = {
    "summary": "string",
    "findings": [
        {
            "category": (
                "website|business_model|services|technology|pain_points|tools|buying_signals"
            ),
            "statement": "string",
            "confidence": "verified|inferred|unknown",
            "evidence": "string|null",
        }
    ],
    "pain_points": ["string"],
    "buying_signals": ["string"],
}


def build_user_prompt(lead: dict[str, Any], context: str) -> str:
    lead_lines = "\n".join(f"- {key}: {value}" for key, value in lead.items())
    return (
        "Research this business.\n\nLEAD:\n"
        f"{lead_lines}\n\nCONTEXT:\n{context or 'No additional context provided.'}"
    )
