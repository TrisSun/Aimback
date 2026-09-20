from __future__ import annotations

from typing import Protocol


class EmbeddingError(Exception):
    """供应商调用失败。"""


class EmbeddingProvider(Protocol):
    name: str

    def is_available(self) -> bool:
        """是否具备调用条件（如 API Key）。"""

    def embed(self, *, text: str, image_url: str | None = None) -> list[float]:
        """返回 L2 可归一化的向量。image_url 为空时走纯文本。"""
