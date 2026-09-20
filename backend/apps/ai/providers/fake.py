from __future__ import annotations

import hashlib

from apps.ai import constants


class FakeProvider:
    """确定性假向量，测试与无 Key 环境使用，不访问外网。"""

    name = constants.PROVIDER_FAKE

    def is_available(self) -> bool:
        return True

    def embed(self, *, text: str, image_url: str | None = None) -> list[float]:
        seed = f"{text}|{image_url or ''}".encode("utf-8")
        digest = hashlib.sha256(seed).digest()
        vector = [0.0] * constants.EMBEDDING_DIM
        for i in range(0, min(len(digest), constants.EMBEDDING_DIM)):
            vector[i] = (digest[i] - 127.5) / 127.5
        # 让相同前缀文本在前几维更接近，便于手工构造测试。
        lowered = (text or "").lower()
        if "phone" in lowered or "手机" in lowered:
            vector[0] = 1.0
        if "wallet" in lowered or "钱包" in lowered:
            vector[1] = 1.0
        return vector
