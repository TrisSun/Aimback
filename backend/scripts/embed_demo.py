"""百炼多模态融合向量最小 demo。不依赖 Django，可在 2 核 4G 服务器上直接跑。

用法（在 backend/ 目录、已激活 venv）：
    python scripts/embed_demo.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
load_dotenv(SCRIPT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env")

MODEL = "tongyi-embedding-vision-flash-2026-03-06"
DIMENSION = 512
SAMPLE_TEXT = "图书馆三楼捡到一部黑色手机，背面有贴纸"
SAMPLE_IMAGE = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/256_1.png"


def _configure_dashscope(api_key: str) -> None:
    import dashscope

    dashscope.api_key = api_key
    workspace = os.getenv("DASHSCOPE_WORKSPACE_ID", "").strip()
    if workspace:
        dashscope.base_http_api_url = (
            f"https://{workspace}.cn-beijing.maas.aliyuncs.com/api/v1"
        )


def _embed(contents: list[dict]) -> object:
    import dashscope

    return dashscope.MultiModalEmbedding.call(
        model=MODEL,
        input=contents,
        dimension=DIMENSION,
    )


def _report(title: str, resp: object) -> bool:
    status = getattr(resp, "status_code", None)
    code = getattr(resp, "code", "")
    message = getattr(resp, "message", "")
    print(f"\n=== {title} ===")
    print(f"status_code={status} code={code} message={message}")
    if status != 200:
        return False
    embeddings = resp.output["embeddings"]
    print(f"count={len(embeddings)}")
    for item in embeddings:
        vector = item["embedding"]
        print(f"  type={item.get('type')} dim={len(vector)}")
        if len(vector) != DIMENSION:
            print(f"  警告：期望 {DIMENSION} 维，实际 {len(vector)}")
            return False
    return True


def main() -> int:
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        print("DASHSCOPE_API_KEY 为空。请写在 backend/.env，不要提交到 git。")
        return 1

    try:
        import dashscope  # noqa: F401
    except ImportError:
        print("未安装 dashscope。先执行: pip install dashscope python-dotenv")
        return 1

    _configure_dashscope(api_key)
    print(f"model={MODEL} dimension={DIMENSION}")

    cases = [
        ("文+图融合（入库主路径）", [{"text": SAMPLE_TEXT, "image": SAMPLE_IMAGE}]),
        ("仅文字（无图帖退化）", [{"text": SAMPLE_TEXT}]),
        (
            "同一描述 + 两张图（多视图）",
            [
                {"text": SAMPLE_TEXT, "image": SAMPLE_IMAGE},
                {"text": SAMPLE_TEXT, "image": SAMPLE_IMAGE},
            ],
        ),
    ]

    ok = True
    for title, contents in cases:
        resp = _embed(contents)
        if not _report(title, resp):
            ok = False

    if ok:
        print("\n全部通过。可以开始建 apps/ai/。")
        return 0
    print("\n有失败项。把上面的 status_code / code / message 原文留下来排查。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
