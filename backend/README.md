# Aimback 后端（Django + DRF）

本目录是团队共用的 Django 工程。A 负责项目骨架与 `apps/posts`，B/C/E 在
各自 app 目录内开发，不要修改别人的 app 文件。

## 本地启动

```bash
cd backend
python -m venv .venv
# Windows（MSYS2 环境）
source .venv/bin/activate
# Windows（原生 PowerShell）
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

管理后台：`/admin/`。帖子接口基地址：`/api/v1/posts`。

## 测试

```bash
python manage.py test apps.posts
```

## 目录归属

| 目录 | 负责人 |
| --- | --- |
| `apps/posts/` | A |
| `apps/accounts/`、`apps/storage/` | B |
| `apps/claims/` | C |
| `apps/ai/` | E |
| `config/`、`requirements.txt` | A 主导 |

## 首日约定

- 目前使用内置 `auth.User` 验证 posts 迁移；B 建立 `apps.accounts.User`
  后，将 `settings.AUTH_USER_MODEL` 指向 `accounts.User`，posts 迁移会跟随
  切换，不要在未对齐前自行改 `AUTH_USER_MODEL`。
- 数据库默认 SQLite；PostgreSQL/pgvector 与部署由 B 在 `infra/` 落地。
- 图片访问链接由 B 的 COS 签名凭证服务生成，帖子序列化器中暂返回 `null`。
- 迁移只针对自己的 app 执行，例如 `python manage.py makemigrations posts`。
