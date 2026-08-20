"""
storage.cos_presign
封装 COS 凭证：上传预签名（含跨桶缩略图）、原图签名读、缩略图公有 URL。

双桶设计（接口契约）：
    - 原图桶（私有读）：存原始大图，仅通过后端签名 URL 下发
    - 缩略图桶（公有读）：存缩略图，前端直连访问

缩略图生成采用「上传时处理」：前端 PUT 原图时携带 Pic-Operations 头，
COS 上传完成后自动把缩略图写入公有桶，一次上传同时产出两份对象。

key 约定：
    - 原图 cos_key：posts/YYYY/MM/{uuid}.{ext}（ext 由 Content-Type 推导）
    - 缩略图 key：  posts/YYYY/MM/{uuid}_thumb.jpg（强制 jpg）
"""
import json
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from qcloud_cos import CosConfig, CosS3Client

load_dotenv()

# Content-Type -> 原图 key 后缀
CONTENT_TYPE_TO_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/bmp": "bmp",
}

THUMB_MAX_EDGE = 400  # 缩略图最长边（像素）
THUMB_QUALITY = 80    # 缩略图压缩质量（仅 jpg/webp 生效）
UPLOAD_EXPIRES = 300  # 上传凭证有效期（秒）


def _client() -> CosS3Client:
    cfg = CosConfig(
        Region=os.environ["COS_REGION"],
        SecretId=os.environ["COS_SECRET_ID"],
        SecretKey=os.environ["COS_SECRET_KEY"],
        Scheme="https",
    )
    return CosS3Client(cfg)


def _make_key(content_type: str) -> str:
    """原图 key：posts/YYYY/MM/{uuid}.{ext}"""
    ext = CONTENT_TYPE_TO_EXT.get(content_type, "jpg")
    now = datetime.utcnow()
    return f"posts/{now:%Y}/{now:%m}/{uuid.uuid4().hex}.{ext}"


def thumb_key_for(original_key: str) -> str:
    """原图 key -> 缩略图 key：posts/.../uuid.png -> posts/.../uuid_thumb.jpg"""
    stem, _ = os.path.splitext(original_key)
    return f"{stem}_thumb.jpg"


def _thumb_rule() -> str:
    """数据万象图片处理规则：等比缩放 + 转 jpg + 压缩"""
    return (
        f"imageMogr2/thumbnail/{THUMB_MAX_EDGE}x{THUMB_MAX_EDGE}"
        f"/format/jpg/quality/{THUMB_QUALITY}"
    )


def presign_original_upload(content_type: str = "image/jpeg") -> dict:
    """
    返回前端上传所需的「一次性凭证」：
    - 5 分钟有效
    - 对象 key 由后端指定（前端不自拼）
    - 原图进私有桶；Pic-Operations 头让 COS 上传后自动生成缩略图到公有桶
    - 前端 PUT 时必须原样携带 headers 里这两个字段，否则签名校验失败
    """
    original_bucket = os.environ["COS_BUCKET_ORIGINAL"]
    thumb_bucket = os.environ["COS_BUCKET_THUMB"]
    region = os.environ["COS_REGION"]

    key = _make_key(content_type)
    thumb_key = thumb_key_for(key)

    pic_ops = {
        "is_pic_info": 0,
        "rules": [
            {
                "fileid": f"/{thumb_key}",
                "rule": _thumb_rule(),
                "bucket": thumb_bucket,
            }
        ],
    }

    # 这两个 header 会算入签名，前端上传时必须原样携带（值完全一致）
    headers = {
        "Content-Type": content_type,
        "Pic-Operations": json.dumps(pic_ops, ensure_ascii=False),
    }

    # 注意：get_presigned_url 会原地往传入的 Headers 里追加 Authorization 字段，
    # 因此传一份副本进去，避免污染返回给前端的 headers（前端不需要也不能发 Authorization）。
    url = _client().get_presigned_url(
        Bucket=original_bucket,
        Key=key,
        Method="PUT",
        Expired=UPLOAD_EXPIRES,
        Headers=dict(headers),
    )

    return {
        "bucket": original_bucket,
        "region": region,
        "cos_key": key,          # 前端 PUT 完后回传给 A 的帖子接口
        "thumb_key": thumb_key,  # 缩略图 key（调试用，前端无需关心）
        "upload_url": url,
        "method": "PUT",
        "headers": headers,
        "expires_in": UPLOAD_EXPIRES,
    }


def presign_original_get(key: str, expired: int = 600) -> str:
    """原图私有桶签名读 URL（详情页展示原图用，短时有效）"""
    bucket = os.environ["COS_BUCKET_ORIGINAL"]
    return _client().get_presigned_url(
        Bucket=bucket,
        Key=key,
        Method="GET",
        Expired=expired,
    )


def thumb_url_for(original_key: str) -> str:
    """缩略图公有桶直连 URL（列表页用，公有读无需签名）"""
    bucket = os.environ["COS_BUCKET_THUMB"]
    region = os.environ["COS_REGION"]
    return f"https://{bucket}.cos.{region}.myqcloud.com/{thumb_key_for(original_key)}"
