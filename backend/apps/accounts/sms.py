"""
短信验证码（自管校验 + 多通道发送）。

大纲指定使用阿里云 PNVS「短信认证」发送验证码。
PNVS 的 CheckSmsVerifyCode 在我们账号上持续 isv.ValidateFail，
因此采用混合模式：PNVS 发送（return_verify_code=True 拿回码）+ 本地 cache 校验。

通道优先级：PNVS > dysms > tencent > console(dev)
  - pnvs    阿里云号码认证服务（大纲指定），免签名/模板，个人实名即可
  - dysms   阿里云普通短信服务（备选），需自申签名+模板
  - tencent 腾讯云短信（备选），TODO
  - console 开发模式，验证码在响应 dev_code 返回

校验逻辑统一走本地 Django cache（5 分钟 TTL，一次性）。
"""
import json
import logging
import os
import random

log = logging.getLogger(__name__)

CODE_TTL = 300  # 5 分钟


def _random_code() -> str:
    return f"{random.randint(0, 999999):06d}"


# ===== 阿里云 PNVS（大纲指定通道）=====================================

_pnvs_client = None


def _get_pnvs_client():
    global _pnvs_client
    if _pnvs_client is not None:
        return _pnvs_client
    from alibabacloud_dypnsapi20170525.client import Client as PnvsClient
    from alibabacloud_tea_openapi import models as open_api_models

    config = open_api_models.Config(
        access_key_id=os.environ.get("ALIYUN_PNVS_ACCESS_KEY_ID"),
        access_key_secret=os.environ.get("ALIYUN_PNVS_ACCESS_KEY_SECRET"),
    )
    config.endpoint = "dypnsapi.aliyuncs.com"
    _pnvs_client = PnvsClient(config)
    return _pnvs_client


def _send_via_pnvs(phone):
    """
    调 PNVS SendSmsVerifyCode 发送验证码。
    return_verify_code=True 让阿里云把生成的码回传给后端，
    后端存 cache 后用本地校验（绕开 isv.ValidateFail 的 CheckSmsVerifyCode）。
    返回 (ok, code_or_None, err_or_None)。
    """
    from alibabacloud_dypnsapi20170525 import models as pnvs_models

    try:
        resp = _get_pnvs_client().send_sms_verify_code(
            pnvs_models.SendSmsVerifyCodeRequest(
                phone_number=phone,
                sign_name=os.environ.get("ALIYUN_PNVS_SIGN_NAME"),
                template_code=os.environ.get("ALIYUN_PNVS_TEMPLATE_CODE"),
                code_type=1,             # 纯数字
                code_length=6,           # 6 位
                valid_time=5,            # 5 分钟有效
                interval=60,             # 同号 60s 重发间隔
                return_verify_code=True, # 拿回码做本地校验
                template_param='{"code":"##code##","min":"5"}',
            )
        )
        body = resp.body.to_map() if hasattr(resp.body, "to_map") else {}
        if not body.get("Success", True):
            return False, None, f"{body.get('Code')}: {body.get('Message')}"
        code = body.get("VerifyCode") or body.get("Model", {}).get("VerifyCode")
        if not code:
            return False, None, "PNVS 返回成功但未带回验证码"
        log.info("PNVS send ok phone=%s code=%s", phone[-4:], code)
        return True, code, None
    except Exception as e:
        msg = getattr(e, "message", None) or str(e)
        log.warning("PNVS send fail phone=%s err=%s", phone[-4:], msg)
        return False, None, msg


# ===== 阿里云 dysms（备选通道）=======================================

_dysms_client = None


def _get_dysms_client():
    global _dysms_client
    if _dysms_client is not None:
        return _dysms_client
    from alibabacloud_dysmsapi20170525.client import Client as DysmsClient
    from alibabacloud_tea_openapi import models as open_api_models

    config = open_api_models.Config(
        access_key_id=os.environ.get("ALIYUN_DYSMS_ACCESS_KEY_ID"),
        access_key_secret=os.environ.get("ALIYUN_DYSMS_ACCESS_KEY_SECRET"),
    )
    config.endpoint = "dysmsapi.aliyuncs.com"
    _dysms_client = DysmsClient(config)
    return _dysms_client


def _send_via_dysms(phone, code):
    from alibabacloud_dysmsapi20170525 import models as dysms_models

    try:
        resp = _get_dysms_client().send_sms(
            dysms_models.SendSmsRequest(
                phone_numbers=phone,
                sign_name=os.environ.get("ALIYUN_DYSMS_SIGN_NAME"),
                template_code=os.environ.get("ALIYUN_DYSMS_TEMPLATE_CODE"),
                template_param=json.dumps({"code": code}),
            )
        )
        body = resp.body
        if body.code == "OK":
            log.info("dysms send ok phone=%s", phone[-4:])
            return True, None
        return False, f"{body.code}: {body.message}"
    except Exception as e:
        msg = getattr(e, "message", None) or str(e)
        log.warning("dysms send fail phone=%s err=%s", phone[-4:], msg)
        return False, msg


# ===== 通道选择 ========================================================

def _select_channel():
    """
    返回 (channel_name)。
    优先级：PNVS > dysms > console(dev)
    """
    if os.environ.get("ALIYUN_PNVS_ACCESS_KEY_ID") and os.environ.get("ALIYUN_PNVS_ACCESS_KEY_SECRET"):
        return "pnvs"
    if os.environ.get("ALIYUN_DYSMS_ACCESS_KEY_ID") and os.environ.get("ALIYUN_DYSMS_ACCESS_KEY_SECRET"):
        return "dysms"
    return "console"


def is_configured() -> bool:
    return _select_channel() != "console"


# ===== 对外 API =======================================================

def send_code(phone, cache_backend):
    """
    发送验证码并存入 cache。返回 (ok, code_or_None, err_or_None)。

    - PNVS：阿里云生成码 → 发 SMS → 回传码 → 存 cache
    - dysms：本地生成码 → 存 cache → 发 SMS
    - console(dev)：本地生成码 → 存 cache → 返回码（响应 dev_code）
    """
    channel = _select_channel()
    key = f"sms:code:{phone}"

    if channel == "pnvs":
        ok, code, err = _send_via_pnvs(phone)
        if ok and code:
            cache_backend.set(key, code, CODE_TTL)
            return True, code, None
        return False, None, err

    # dysms / console：本地生成
    code = _random_code()
    cache_backend.set(key, code, CODE_TTL)

    if channel == "console":
        log.warning("[DEV] phone=%s code=%s", phone, code)
        return True, code, None

    # dysms
    ok, err = _send_via_dysms(phone, code)
    if not ok:
        return False, None, err
    return True, code, None


def verify(phone, code, cache_backend):
    """校验用户提交的码。匹配则删除 cache（一次性）。"""
    key = f"sms:code:{phone}"
    real = cache_backend.get(key)
    if not real or real != code:
        return False
    cache_backend.delete(key)
    return True
