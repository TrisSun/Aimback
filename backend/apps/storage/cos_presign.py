"""
storage.cos_presign
封装 COS 凭证：拿到环境变量、用 SDK 生成一次性预签名 URL。

接口契约约定：
    cos_key 路径：posts/YYYY/MM/{uuid}.jpg（原图进私有桶）
    契约 3.5：images 最多 4 张
"""
import os
import uuid
from datetime import datetime

from qcloud_cos import CosConfig, CosS3Client
from dotenv import load_dotenv

load_dotenv()


def _client():
    cfg = CosConfig(
        Region=os.environ["COS_REGION"],
        SecretId=os.environ["COS_SECRET_ID"],
        SecretKey=os.environ["COS_SECRET_KEY"],
        Scheme="https",
    )
    return CosS3Client(cfg)


def _make_key(ext: str = "jpg") -> str:
    """按契约格式返回 cos_key：posts/YYYY/MM/uuid.ext"""
    safe_ext = ext.lstrip(".").lower() or "jpg"
    now = datetime.utcnow()
    return f"posts/{now:%Y}/{now:%m}/{uuid.uuid4().hex}.{safe_ext}"


def presign_original_upload(content_type: str = "image/jpeg") -> dict:
    """
    返回前端上传所需的「一次性凭证」：
    - 5 分钟有效
    - 对象 key 由后端指定（前端不自拼）
    - 原图进私有桶（契约要求）
    """
    bucket = os.environ["COS_BUCKET_ORIGINAL"]
    region = os.environ["COS_REGION"]
    key = _make_key("jpg")

    url = _client().get_presigned_url(
        Bucket=bucket,
        Key=key,
        Method="PUT",
        Expired=300,
        Headers={"Content-Type": content_type},
    )

    return {
        "bucket": bucket,
        "region": region,
        "cos_key": key,         # 前端 PUT 完后回传给 A 的帖子接口
        "upload_url": url,
        "method": "PUT",
        "headers": {"Content-Type": content_type},
        "expires_in": 300,
    }


def public_url_for(bucket: str, key: str) -> str:
    """缩略图（公有读）→ 浏览器直访 URL。前端不可自拼（契约 :11）。"""
    region = os.environ["COS_REGION"]
    return f"https://{bucket}.cos.{region}.myqcloud.com/{key}"