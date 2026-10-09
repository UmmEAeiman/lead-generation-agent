"""Research Agent: analyze a business from evidence only."""

from typing import Any

from app.agents.base import BaseAgent
from app.agents.results import ResearchResult
from app.prompts import research as prompt

_VALID_CONFIDENCE = {"verified", "inferred", "unknown"}
_VALID_CATEGORIES = {
    "website",
    "business_model",
    "services",
    "technology",
    "pain_points",
    "tools",
    "buying_signals",
}


class ResearchAgent(BaseAgent):
    name = "research"

    async def run(self, lead: dict[str, Any], context: str = "") -> ResearchResult:
        response = await self.chat_json(
            system=prompt.ROLE,
            user=prompt.build_user_prompt(lead, context),
            output_schema=prompt.OUTPUT_SCHEMA,
        )
        if response and isinstance(response.get("summary"), str):
            findings = []
            for raw in response.get("findings") or []:
                if not isinstance(raw, dict):
                    continue
                confidence = str(raw.get("confidence", "unknown")).lower()
                category = str(raw.get("category", "services"))
                findings.append(
                    {
                        "category": category if category in _VALID_CATEGORIES else "services",
                        "statement": str(raw.get("statement", ""))[:500],
                        "confidence": confidence if confidence in _VALID_CONFIDENCE else "unknown",
                        "evidence": raw.get("evidence"),
                    }
                )
            pain_points = [str(p)[:300] for p in (response.get("pain_points") or [])][:10]
            buying_signals = [str(s)[:300] for s in (response.get("buying_signals") or [])][:10]
            return ResearchResult(
                summary=str(response["summary"])[:1000],
                findings=findings,
                pain_points=pain_points,
                buying_signals=buying_signals,
                used_llm=True,
            )

        return self._fallback_research(lead)

    def _fallback_research(self, lead: dict[str, Any]) -> ResearchResult:
        """Offline research: only restates observed fields as facts."""
        findings: list[dict[str, Any]] = []
        summary_parts: list[str] = []

        industry = lead.get("industry")
        location = lead.get("location")
        if industry:
            summary_parts.append(f"Industry: {industry}.")
            findings.append(
                {
                    "category": "business_model",
                    "statement": f"Listed industry: {industry}",
                    "confidence": "verified",
                    "evidence": "lead.industry",
                }
            )
        if location:
            summary_parts.append(f"Location: {location}.")
        if lead.get("website"):
            findings.append(
                {
                    "category": "website",
                    "statement": f"Website on file: {lead['website']}",
                    "confidence": "verified",
                    "evidence": "lead.website",
                }
            )
        else:
            findings.append(
                {
                    "category": "website",
                    "statement": "No website on file",
                    "confidence": "unknown",
                    "evidence": None,
                }
            )

        if not summary_parts:
            summary_parts.append("Insufficient data for research.")
        summary_parts.append(
            "LLM research not configured; only observed lead fields are reported."
        )
        return ResearchResult(
            summary=" ".join(summary_parts)[:1000],
            findings=findings,
            pain_points=[],
            buying_signals=[],
            used_llm=False,
        )
