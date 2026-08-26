# The Food Master

本地生活平台（美食外卖 / 酒店 / 娱乐 / 博客 / AI 助手），Django + MySQL。

## 仓库结构

```text
docs/          需求、设计、用例追溯
src/           应用源码（manage.py、food_master、myapp、templates、static）
test/          自动化测试
docker/        容器与 Nginx 配置
data_hex2.sql  初始 MySQL 数据
DEPLOY.md      公网 Docker 部署说明
```

## 本地运行

1. 安装依赖（仓库根目录）：

```powershell
pip install -r requirements.txt
```

2. 准备 MySQL（库名 `the_food_mas2`）：

```powershell
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS the_food_mas2 DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

导入数据请用 **cmd**（PowerShell 的 `<` 重定向不可用）：

```cmd
mysql -u root -p --binary-mode the_food_mas2 < data_hex2.sql
```

3. 配置数据库账号：改 `src/food_master/settings.py`，或设置 `FOOD_DELIVER_DB_*` 环境变量 / `.env`。

4. 启动：

```powershell
cd src
python manage.py runserver
```

浏览器打开 http://127.0.0.1:8000/

## 主要功能

- 多角色：普通用户、骑手、商家、管理员
- 美食外卖全链路（下单 → 接单 → 备餐 → 配送 → 评价）
- 到店团购、酒店预订、娱乐购票
- 购物车、列表搜索与排序
- 博客、AI 助手、管理后台

## 其它文档

| 文档 | 内容 |
|------|------|
| [DEPLOY.md](DEPLOY.md) | Docker Compose 公网部署 |
| [docs/USE_CASE_TRACEABILITY.md](docs/USE_CASE_TRACEABILITY.md) | 用例说明与需求/代码/测试追溯 |
| [test/README.md](test/README.md) | 自动化测试说明 |

表结构以 `src/myapp/models.py` 为准。
