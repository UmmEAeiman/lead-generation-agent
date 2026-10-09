"""Text embedding with a deterministic offline embedder.

A provider-backed embedder can replace `embed_texts` later; the signature and
the pgvector column stay the same (vendor-agnostic boundary).
"""

import hashlib
import math
import re

from app.core.config import settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def embed_text(text: str, dim: int | None = None) -> list[float]:
    dimension = dim or settings.embedding_dim
    vector = [0.0] * dimension
    tokens = _tokenize(text)
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return [round(v, 7) for v in vector]


def embed_texts(texts: list[str], dim: int | None = None) -> list[list[float]]:
    return [embed_text(t, dim) for t in texts]


def embed_lead_text(parts: list[str | None]) -> list[float]:
    joined = " | ".join(p.strip() for p in parts if p and p.strip())
    return embed_text(joined)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return round(dot / (norm_a * norm_b), 6)
