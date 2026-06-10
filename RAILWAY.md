# Railway 部署说明

本项目已经支持 Railway 的 MySQL 环境变量和 `PORT` 端口变量。

## 部署步骤

1. 打开 Railway，新建 Project。
2. 选择 `Deploy from GitHub repo`，选择本仓库。
3. 在同一个 Project 里添加 MySQL 服务。
4. 打开 Django/Web 服务的 Variables，添加：

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=换成一个很长的随机字符串
IMPORT_SQL_ON_START=true
MYSQLHOST=${{ MySQL.MYSQLHOST }}
MYSQLPORT=${{ MySQL.MYSQLPORT }}
MYSQLUSER=${{ MySQL.MYSQLUSER }}
MYSQLPASSWORD=${{ MySQL.MYSQLPASSWORD }}
MYSQLDATABASE=${{ MySQL.MYSQLDATABASE }}
```

如果需要 AI 聊天功能，再添加：

```text
ALIYUN_API_KEY=你的 DashScope Key
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

5. 在 Django/Web 服务里进入 Settings -> Networking -> Public Networking，点击 Generate Domain。
6. 等待重新部署完成，访问 Railway 生成的网址。

## 数据库初始化

首次启动时，如果 MySQL 中还没有 `django_migrations` 表，容器会自动导入仓库里的 `data_hex2.sql`，然后执行 `python manage.py migrate`。

如需禁用自动导入，把变量改成：

```text
IMPORT_SQL_ON_START=false
```
