from __future__ import annotations

import os

from apps.ai import constants
from apps.ai.providers.base import EmbeddingError


class DashscopeProvider:
    """阿里云百炼多模态 Embedding，调用方式与 scripts/embed_demo.py 对齐。"""

    name = constants.PROVIDER_DASHSCOPE

    def is_available(self) -> bool:
        return bool(os.environ.get("DASHSCOPE_API_KEY", "").strip())

    def embed(self, *, text: str, image_url: str | None = None) -> list[float]:
        import dashscope

        api_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
        if not api_key:
            raise EmbeddingError("DASHSCOPE_API_KEY 为空")

        dashscope.api_key = api_key
        workspace = os.environ.get("DASHSCOPE_WORKSPACE_ID", "").strip()
        if workspace:
            dashscope.base_http_api_url = (
                f"https://{workspace}.cn-beijing.maas.aliyuncs.com/api/v1"
            )

        content: dict[str, str] = {}
        if text.strip():
            content["text"] = text.strip()
        if image_url:
            content["image"] = image_url
        if not content:
            raise EmbeddingError("文本与图片均为空，无法向量化")

        resp = dashscope.MultiModalEmbedding.call(
            model=constants.MODEL_DASHSCOPE,
            input=[content],
            dimension=constants.EMBEDDING_DIM,
        )
        status = getattr(resp, "status_code", None)
        if status != 200:
            code = getattr(resp, "code", "")
            message = getattr(resp, "message", "")
            raise EmbeddingError(f"百炼返回 {status} {code}: {message}")

        embeddings = (getattr(resp, "output", None) or {}).get("embeddings") or []
        if not embeddings:
            raise EmbeddingError("百炼未返回 embeddings")
        vector = embeddings[0].get("embedding")
        if not isinstance(vector, list) or len(vector) != constants.EMBEDDING_DIM:
            actual = len(vector) if isinstance(vector, list) else type(vector)
            raise EmbeddingError(f"向量维度异常：期望 {constants.EMBEDDING_DIM}，实际 {actual}")
        return [float(x) for x in vector]
