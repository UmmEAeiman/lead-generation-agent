"""Qualification Agent: explicit, configurable scoring (0-100)."""

from dataclasses import dataclass
from typing import Any

from app.agents.base import BaseAgent
from app.agents.results import QualificationResult
from app.prompts import qualification as prompt


@dataclass(frozen=True)
class ScoringCriteria:
    """Points must always sum to 100 (constitution §9)."""

    icp_fit: int = 25
    company_size: int = 15
    industry_fit: int = 20
    buying_signal: int = 20
    pain_point: int = 10
    contact_quality: int = 10

    @property
    def caps(self) -> dict[str, int]:
        return {
            "icp_fit": self.icp_fit,
            "company_size": self.company_size,
            "industry_fit": self.industry_fit,
            "buying_signal": self.buying_signal,
            "pain_point": self.pain_point,
            "contact_quality": self.contact_quality,
        }

    @property
    def total(self) -> int:
        return sum(self.caps.values())


DEFAULT_CRITERIA = ScoringCriteria()


def band_for_score(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _contains(haystack: Any, needle: Any) -> bool:
    if not needle:
        return False
    return str(needle).strip().lower() in str(haystack or "").strip().lower()


def _sizes_overlap(left: Any, right: Any) -> bool:
    if not left or not right:
        return False
    return str(left).strip().lower() == str(right).strip().lower()


def score_lead(
    lead: dict[str, Any],
    icp: dict[str, Any],
    research: dict[str, Any] | None = None,
    criteria: ScoringCriteria = DEFAULT_CRITERIA,
) -> QualificationResult:
    """Deterministic rules-based scoring. Pure and independently testable."""
    research = research or {}
    breakdown: dict[str, int] = {}
    reasons: list[str] = []

    industry_target = icp.get("industry") or icp.get("target_industry")
    location_target = icp.get("location") or icp.get("target_location")
    size_target = icp.get("company_size") or icp.get("target_company_size")
    keywords = [str(k) for k in icp.get("keywords") or []]

    # Industry fit (20)
    if industry_target:
        matched = _contains(lead.get("industry"), industry_target) or _contains(
            industry_target, lead.get("industry")
        )
        breakdown["industry_fit"] = criteria.industry_fit if matched else 0
        reasons.append(
            f"Industry '{lead.get('industry') or 'unknown'}' vs ICP "
            f"'{industry_target}': {'match' if matched else 'no match'} "
            f"({breakdown['industry_fit']}/{criteria.industry_fit})."
        )
    else:
        breakdown["industry_fit"] = 0
        reasons.append(f"No ICP industry defined: 0/{criteria.industry_fit}.")

    # ICP fit (25): location 15 + keyword relevance 10
    icp_fit = 0
    if location_target:
        location_match = _contains(lead.get("location"), location_target)
        icp_fit += 15 if location_match else 0
        reasons.append(
            f"Location '{lead.get('location') or 'unknown'}': "
            f"{'matches' if location_match else 'does not match'} ICP '{location_target}'."
        )
    else:
        reasons.append("No ICP location defined (0/15).")
    searchable = " ".join(
        str(lead.get(field) or "") for field in ("company_name", "description", "industry")
    )
    keyword_hit = any(_contains(searchable, k) for k in keywords)
    if keywords:
        icp_fit += 10 if keyword_hit else 0
        reasons.append(f"Keyword relevance: {'found' if keyword_hit else 'not found'} (0-10).")
    else:
        reasons.append("No ICP keywords defined (0/10).")
    breakdown["icp_fit"] = min(icp_fit, criteria.icp_fit)

    # Company size (15)
    if size_target:
        size_match = _sizes_overlap(lead.get("company_size"), size_target)
        breakdown["company_size"] = criteria.company_size if size_match else 0
        reasons.append(
            f"Company size '{lead.get('company_size') or 'unknown'}' vs ICP "
            f"'{size_target}': {'match' if size_match else 'no match'}."
        )
    else:
        breakdown["company_size"] = 0
        reasons.append("No ICP company size defined (0/15).")

    # Buying signals (20): 10 points each, capped
    signals = [str(s) for s in research.get("buying_signals") or [] if s]
    breakdown["buying_signal"] = min(len(signals) * 10, criteria.buying_signal)
    if signals:
        observed = breakdown["buying_signal"]
        reasons.append(f"{len(signals)} buying signal(s) observed ({observed}/20).")
    else:
        reasons.append("No buying signal data: 0/20.")

    # Pain points (10)
    pains = [str(p) for p in research.get("pain_points") or [] if p]
    breakdown["pain_point"] = criteria.pain_point if pains else 0
    reasons.append(
        f"Pain points identified: {len(pains)} ({breakdown['pain_point']}/10)."
        if pains
        else "No pain point data: 0/10."
    )

    # Contact quality (10): email 5, contact name 3, role 2
    contact_quality = 0
    if lead.get("email"):
        contact_quality += 5
    if lead.get("contact_name"):
        contact_quality += 3
    if lead.get("contact_role"):
        contact_quality += 2
    breakdown["contact_quality"] = contact_quality
    reasons.append(
        f"Contact quality: email={'yes' if lead.get('email') else 'no'}, "
        f"name={'yes' if lead.get('contact_name') else 'no'}, "
        f"role={'yes' if lead.get('contact_role') else 'no'} ({contact_quality}/10)."
    )

    score = sum(breakdown.values())
    return QualificationResult(
        score=score,
        category=band_for_score(score),  # type: ignore[arg-type]
        breakdown=breakdown,
        reasons=reasons,
        confidence="verified",
        used_llm=False,
    )


class QualificationAgent(BaseAgent):
    name = "qualification"

    def __init__(self, llm: Any = None, criteria: ScoringCriteria = DEFAULT_CRITERIA) -> None:
        super().__init__(llm)
        self.criteria = criteria

    async def run(
        self,
        lead: dict[str, Any],
        icp: dict[str, Any],
        research: dict[str, Any] | None = None,
    ) -> QualificationResult:
        rules_result = score_lead(lead, icp, research, self.criteria)

        response = await self.chat_json(
            system=prompt.ROLE,
            user=prompt.build_user_prompt(lead, icp, research or {}),
            output_schema=prompt.OUTPUT_SCHEMA,
        )
        if not response or not isinstance(response.get("breakdown"), dict):
            return rules_result

        raw_breakdown = response["breakdown"]
        breakdown: dict[str, int] = {}
        for key, cap in self.criteria.caps.items():
            value = raw_breakdown.get(key, 0)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                value = 0
            breakdown[key] = max(0, min(int(value), cap))

        score = sum(breakdown.values())
        reasons = [
            str(r)[:300]
            for r in (response.get("reasons") or [])
            if isinstance(r, str) and r.strip()
        ] or rules_result.reasons
        confidence = str(response.get("confidence", "unverified")).lower()
        if confidence not in {"verified", "unverified", "unknown"}:
            confidence = "unverified"

        return QualificationResult(
            score=score,
            category=band_for_score(score),  # type: ignore[arg-type]
            breakdown=breakdown,
            reasons=reasons,
            confidence=confidence,
            used_llm=True,
        )
