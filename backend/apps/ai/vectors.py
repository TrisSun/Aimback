from __future__ import annotations

import hashlib
import logging
import math

from apps.ai import constants

logger = logging.getLogger(__name__)


def l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return list(vector)
    return [x / norm for x in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    n = min(len(left), len(right))
    if n == 0:
        return 0.0
    dot = 0.0
    norm_l = 0.0
    norm_r = 0.0
    for i in range(n):
        a = float(left[i])
        b = float(right[i])
        dot += a * b
        norm_l += a * a
        norm_r += b * b
    if norm_l <= 0 or norm_r <= 0:
        return 0.0
    value = dot / math.sqrt(norm_l * norm_r)
    return max(-1.0, min(1.0, value))


def cosine_score(left: list[float], right: list[float]) -> float:
    """映射到 [0, 1]，负相似当 0。"""
    return max(0.0, cosine_similarity(left, right))


def source_hash(text: str, image_key: str) -> str:
    payload = f"{constants.EMBEDDING_VERSION}|{text}|{image_key}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
