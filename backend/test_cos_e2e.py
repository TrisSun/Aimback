"""
COS 双桶端到端测试脚本（需真实凭证，配置在 backend/.env）。

用法：
    cd /c/Users/ASUS/Aimback/backend
    C:/Users/ASUS/lostfound-backend/venv/Scripts/python.exe test_cos_e2e.py

流程：
    1. 生成一张 200x200 纯色 PNG 测试图
    2. 调 presign 拿上传凭证（含 Pic-Operations 跨桶缩略图）
    3. PUT 上传原图到私有桶
    4. 验证缩略图公有桶能直接访问（200）
    5. 验证原图私有桶签名读（200）
"""
import os
import struct
import zlib

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests  # noqa: E402

from apps.storage.cos_presign import (  # noqa: E402
    presign_original_get,
    presign_original_upload,
    thumb_url_for,
)


def make_png(width: int, height: int, rgb=(255, 100, 50)) -> bytes:
    """纯 Python 生成一张纯色 PNG（不依赖 Pillow）。"""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8bit RGB
    row = b"\x00" + bytes(rgb) * width
    idat = zlib.compress(row * height)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def main():
    print("=== 1. 生成测试图 200x200 PNG ===")
    img = make_png(200, 200)
    print(f"    测试图大小: {len(img)} bytes")

    print("\n=== 2. presign 拿上传凭证 ===")
    ticket = presign_original_upload("image/png")
    print(f"    cos_key:  {ticket['cos_key']}")
    print(f"    thumb_key:{ticket['thumb_key']}")
    print(f"    headers:  {list(ticket['headers'].keys())}")

    print("\n=== 3. PUT 上传原图到私有桶 ===")
    resp = requests.put(ticket["upload_url"], data=img, headers=ticket["headers"])
    print(f"    上传状态码: {resp.status_code}")
    assert resp.status_code in (200, 204), f"上传失败: {resp.text}"

    print("\n=== 4. 验证缩略图公有桶直连 ===")
    thumb_url = thumb_url_for(ticket["cos_key"])
    resp = requests.get(thumb_url)
    print(f"    缩略图 URL: {thumb_url}")
    print(f"    状态码: {resp.status_code}, content-type: {resp.headers.get('content-type')}")
    assert resp.status_code == 200, "缩略图无法访问（检查缩略图桶是否公有读）"

    print("\n=== 5. 验证原图私有桶签名读 ===")
    original_url = presign_original_get(ticket["cos_key"])
    resp = requests.get(original_url)
    print(f"    原图签名 URL: {original_url[:90]}...")
    print(f"    状态码: {resp.status_code}, content-type: {resp.headers.get('content-type')}")
    assert resp.status_code == 200, "原图签名读失败"

    print("\n✅ COS 双桶端到端测试全部通过！")
    print(f"    原图(私有桶): {ticket['cos_key']}")
    print(f"    缩略图(公有桶): {ticket['thumb_key']}")


if __name__ == "__main__":
    main()
