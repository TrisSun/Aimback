# Aimback Web

Vue 3 + TypeScript + Vite 前端，对接 `/api/v1`。

## 本地开发

先启动 Django（默认 `http://127.0.0.1:8000`），再：

```sh
npm install
npm run dev
```

Vite 会把 `/api` 代理到后端。也可用 `.env` 覆盖：

```
VITE_API_BASE=/api/v1
```

## 页面

| 路径 | 说明 |
| --- | --- |
| `/` | 公开信息流（筛选、分页） |
| `/detail/:id` | 详情、认领、作者审核 |
| `/login` | 手机号验证码登录 |
| `/publish` | 发布（登录后） |
| `/search` | AI 搜寻（登录后） |
| `/mine` | 我的帖子 / 认领 |

发布前请在 Django Admin 准备好 `Region` / `Place`。图片直传腾讯云 COS；本地未配置 COS 时可先不传图。AI 搜寻需要后端已运行 `process_embeddings`。
