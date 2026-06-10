# 公网部署说明

这套部署方案使用 Docker Compose 启动 3 个服务：Django/Gunicorn、MySQL 8、Nginx。

## 1. 准备服务器

推荐使用 Ubuntu 22.04 或 24.04 云服务器，放通安全组/防火墙的 80 端口。登录服务器后安装 Docker：

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

重新登录一次，让 Docker 用户组生效。

## 2. 上传项目

把本项目上传到服务器，例如：

```bash
git clone <你的仓库地址> final_work
cd final_work
```

如果不用 Git，也可以把整个项目目录上传到服务器。

## 3. 配置环境变量

```bash
cp .env.example .env
nano .env
```

至少修改这些值：

- `DJANGO_SECRET_KEY`：改成长随机字符串。
- `DJANGO_ALLOWED_HOSTS`：填写你的域名或公网 IP，多个用英文逗号分隔。
- `DJANGO_CSRF_TRUSTED_ORIGINS`：填写 `http://域名` 或 `http://公网IP`。
- `MYSQL_ROOT_PASSWORD` 和 `FOOD_DELIVER_DB_PASSWORD`：改成强密码。
- `ALIYUN_API_KEY`：如果需要 AI 聊天功能，在这里填写；不需要可留空。

## 4. 启动

```bash
docker compose up -d --build
```

首次启动会自动：

- 创建 MySQL 数据库 `the_food_mas2`。
- 导入 `data_hex2.sql`。
- 收集 Django 静态文件。
- 执行数据库迁移。
- 通过 Nginx 暴露公网 80 端口。

访问：

```text
http://你的公网IP/
```

## 5. 常用维护命令

查看运行状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f web
docker compose logs -f nginx
docker compose logs -f db
```

重启：

```bash
docker compose restart
```

停止：

```bash
docker compose down
```

如果要清空数据库并重新导入 SQL：

```bash
docker compose down -v
docker compose up -d --build
```

注意：`down -v` 会删除 MySQL 数据卷，线上数据会丢失。

## 6. 绑定域名和 HTTPS

先把域名 A 记录解析到服务器公网 IP，然后把 `.env` 里的 `DJANGO_ALLOWED_HOSTS` 和 `DJANGO_CSRF_TRUSTED_ORIGINS` 改成域名。

需要 HTTPS 时，建议在服务器上用 Caddy 或 Nginx Proxy Manager 做外层反向代理和自动证书；也可以继续扩展本项目里的 `docker/nginx.conf`，接入 Certbot。

启用 HTTPS 后，可以把 `.env` 中这些值改成：

```bash
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```
