# COS 图片存储接入文档（B 负责）

> 本文档覆盖腾讯云 COS 双桶方案的完整接入：整体设计、环境变量、控制台准备、配置流程、接口说明、故障排查、安全上线 Checklist。

## 1. 整体设计

### 1.1 双桶结构

| 桶 | 读权限 | 存什么 | 前端怎么访问 |
| --- | --- | --- | --- |
| 原图桶（`COS_BUCKET_ORIGINAL`） | **私有读** | 原始大图 | 后端签发短时签名 URL |
| 缩略图桶（`COS_BUCKET_THUMB`） | **公有读** | 压缩后的缩略图 | 直接访问（无需签名） |

为什么双桶：

- **原图私有**：失物招领的原图可能拍到敏感信息（身份证、学生证、门禁卡），不能公开裸奔，必须走后端签名限时下发。
- **缩略图公有**：列表页要一次加载几十张小图，如果每张都签名，既慢又浪费请求。公有读让浏览器直接并发拉图，快且省。

### 1.2 缩略图生成方式：上传时处理

采用数据万象（CI）的「上传时处理」：前端 PUT 原图时，请求头里带 `Pic-Operations`，COS 上传完成后**自动把缩略图写进公有桶**。一次上传同时产出两份对象，无需后端再跑异步任务。

### 1.3 key 约定

| 对象 | key 格式 | 示例 |
| --- | --- | --- |
| 原图 | `posts/YYYY/MM/{32位uuid}.{ext}` | `posts/2026/08/ee89....jpg` |
| 缩略图 | `posts/YYYY/MM/{32位uuid}_thumb.jpg` | `posts/2026/08/ee89...._thumb.jpg` |

- 原图后缀由上传时的 `Content-Type` 推导（jpg/png/webp/gif/bmp）。
- 缩略图**强制转 jpg**（`format/jpg`），后缀统一 `_thumb.jpg`。
- 两个桶用**不同的 key 前缀**区分，但都由原图 key 规则推导，前端只认 `cos_key`（原图 key）。

## 2. 必填环境变量

在 `backend/.env` 中配置（模板见 `.env.example`）：

| 变量 | 说明 | 示例 |
| --- | --- | --- |
| `COS_SECRET_ID` | 腾讯云 API 密钥 SecretId | `AKID...` |
| `COS_SECRET_KEY` | 腾讯云 API 密钥 SecretKey | 见控制台 |
| `COS_REGION` | 桶所在地域 | `ap-guangzhou` |
| `COS_BUCKET_ORIGINAL` | 原图桶名（含 AppId） | `lostfound-original-1470644056` |
| `COS_BUCKET_THUMB` | 缩略图桶名（含 AppId） | `lostfound-thumb-1470644056` |

> 桶名格式必须是 `BucketName-AppId`，AppId 在控制台右上角能看到。

## 3. 控制台准备（一次性）

### 3.1 创建两个桶

1. 登录 [COS 控制台](https://console.cloud.tencent.com/cos5/bucket)
2. 创建原图桶：名称如 `lostfound-original`，地域选 `广州`，**访问权限选「私有读写」**
3. 创建缩略图桶：名称如 `lostfound-thumb`，地域选 `广州`，**访问权限选「公有读私有写」**

### 3.2 开通数据万象（缩略图处理依赖它）

1. 进入原图桶 → 左侧「数据处理」→「图片处理」
2. 按提示开通数据万象（免费额度内足够开发测试用）

### 3.3 获取 API 密钥

1. 访问 [API 密钥管理](https://console.cloud.tencent.com/cam/capi)
2. 已有密钥直接用；没有就「新建密钥」
3. 把 `SecretId` / `SecretKey` 抄进 `.env`

> ⚠️ 主账号密钥权限很大，正式上线建议改「子账号 + 最小权限」（见第 7 节）。

### 3.4 授权数据万象服务角色（跨桶处理必需）

跨桶写缩略图时，数据万象需要一个服务角色 `CI_QCSRole` 来访问目标桶。没授权会报 `Qcloud api role not exist, need create role`。

点这个授权链接，登录后点「同意授权」即可：

```
https://console.cloud.tencent.com/cam/role/grant?roleName=CI_QCSRole&policyName=QcloudCOSDataFullControl&principal=eyJzZXJ2aWNlIjoiY2kucWNsb3VkLmNvbSJ9&serviceType=数据万象
```

## 4. 完整配置流程

```bash
cd /c/Users/ASUS/Aimback/backend

# 1. 从模板复制 .env（已 gitignore，不会提交）
cp .env.example .env

# 2. 编辑 .env，填入上面 5 个 COS 变量

# 3. 验证配置加载
C:/Users/ASUS/lostfound-backend/venv/Scripts/python.exe manage.py check
```

## 5. 接口说明

Base URL = `/api/v1`

### 5.1 上传凭证 `POST /api/v1/upload/presign/`

需登录。请求：

```json
{"count": 2, "content_type": "image/jpeg"}
```

响应（每个 ticket 一张图）：

```json
{
  "count": 2,
  "tickets": [
    {
      "bucket": "lostfound-original-1470644056",
      "region": "ap-guangzhou",
      "cos_key": "posts/2026/08/ee89....jpg",
      "thumb_key": "posts/2026/08/ee89...._thumb.jpg",
      "upload_url": "https://...?q-sign-algorithm=sha1&...",
      "method": "PUT",
      "headers": {
        "Content-Type": "image/jpeg",
        "Pic-Operations": "{\"is_pic_info\":0,\"rules\":[...]}"
      },
      "expires_in": 300
    }
  ],
  "expires_in": 300
}
```

### 5.2 访问 URL `GET /api/v1/upload/public-url/`

游客可访问。参数：

| 参数 | 说明 |
| --- | --- |
| `key` | 原图 cos_key（必填） |
| `size` | `thumb`（默认，缩略图直连）/ `original`（原图签名） |

示例：

- 缩略图：`GET /api/v1/upload/public-url/?key=posts/2026/08/ee89....jpg&size=thumb`
- 原图：`GET /api/v1/upload/public-url/?key=posts/2026/08/ee89....jpg&size=original`

响应：

```json
{"url": "https://lostfound-thumb-1470644056.cos.ap-guangzhou.myqcloud.com/posts/2026/08/ee89...._thumb.jpg", "key": "...", "size": "thumb"}
```

## 6. 前端上传注意事项（联调必读）

前端拿到 ticket 后，对 `upload_url` 发 `PUT` 请求时，**必须原样携带 `headers` 里的两个字段**：

```js
fetch(ticket.upload_url, {
  method: "PUT",
  headers: {
    "Content-Type": ticket.headers["Content-Type"],
    "Pic-Operations": ticket.headers["Pic-Operations"],
  },
  body: file, // 图片二进制
});
```

为什么：这两个 header 已经算进签名了，改了任何一个值都会导致 `403 SignatureDoesNotMatch`。

上传完成后，把 `ticket.cos_key` 回传给 A 的帖子接口（契约 §3.5）。

## 7. 安全上线 Checklist

- [ ] 主账号密钥 → 换成**子账号密钥**，只授原图桶 + 缩略图桶的读写权限（最小权限原则）
- [ ] 缩略图桶确认「公有读私有写」，原图桶确认「私有读写」
- [ ] 上传凭证有效期 300 秒够用即可，别调太长
- [ ] `public-url` 接口已做 key 白名单校验（只允许 `posts/YYYY/MM/uuid.ext` 格式）
- [ ] 原图签名 URL 有效期 600 秒，符合「短时签名」要求
- [ ] `.env` 不提交（已在 `.gitignore`），`COS_SECRET_KEY` 绝不进仓库
- [ ] 上线后收紧 CORS（当前 `CORS_ALLOW_ALL_ORIGINS=True` 仅开发用）

## 8. 故障排查速查表

| 现象 | 原因 | 解决 |
| --- | --- | --- |
| 上传报 403 `Qcloud api role not exist, need create role` | 数据万象跨桶处理未授权（缺服务角色 `CI_QCSRole`） | 访问管理授权：点授权链接创建 `CI_QCSRole` 角色（见 3.4） |
| 前端 PUT 报 403 `SignatureDoesNotMatch` | header 没原样携带 / 值被改 | 确认 `Content-Type` 和 `Pic-Operations` 与 ticket 完全一致 |
| 上传成功但缩略图桶没图 | 数据万象未开通 / 跨桶权限不足 | 检查 3.2 是否开通；子账号是否授缩略图桶写权限 |
| 缩略图 URL 直接访问 403 | 缩略图桶不是「公有读」 | 控制台把缩略图桶设为公有读私有写 |
| 原图签名 URL 打不开 | 签名过期（600s）/ key 错误 | 重新请求 `size=original`；核对 cos_key |
| `KeyError: COS_SECRET_ID` | `.env` 没填或没加载 | 确认 `backend/.env` 存在且 5 个变量齐全 |

## 9. 未来扩展点

- **图片审核**：数据万象支持内容审核（鉴黄/涉政），可接 `review_status` 字段做上传后自动审核。
- **CDN 加速**：缩略图桶可挂 CDN，列表页加载更快。
- **格式统一**：原图如需统一转 webp 省流量，可在原图桶侧加处理规则。
- **临时密钥**：用 STS 临时密钥替代永久密钥做上传，进一步缩小泄露面。
