"""Small shared helpers."""

import uuid
from typing import Any


def new_run_id() -> str:
    return f"run_{uuid.uuid4().hex[:20]}"


def compact_summary(data: dict[str, Any], max_len: int = 2000) -> dict[str, Any]:
    """Trim long strings so run summaries stay small and never leak secrets."""
    out: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            out[key] = value if len(value) <= max_len else value[:max_len] + "..."
        elif isinstance(value, list):
            out[key] = value[:20]
        elif isinstance(value, dict):
            out[key] = compact_summary(value, max_len)
        else:
            out[key] = value
    return out
