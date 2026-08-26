# Food Master 综合生活服务平台

本仓库是课程单体基线版本。统一运行基线为 Python 3.10、Django 3.2.11、MySQL 8.0；Docker Compose 和 Kubernetes 均使用 Linux 容器，因此 Windows、macOS、Linux 的启动过程一致。

## 快速启动（推荐）

前提：Docker Desktop 4.x 或 Docker Engine 24+，并启用 Compose v2。

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

Linux/macOS 将第一行替换为 `cp .env.example .env`。首次启动会创建 MySQL 数据库、导入 `data_hex2.sql`、执行迁移并收集静态文件。启动完成后访问：

- 应用入口：<http://localhost/>
- 存活检查：<http://localhost/health/live/>
- 就绪检查（包含数据库连接）：<http://localhost/health/ready/>
- 版本信息：<http://localhost/health/version/>

端口分配：Nginx 对外监听 `80`；Django/Gunicorn 在容器网络监听 `8000`；MySQL 在容器网络监听 `3306`。默认不把后端和数据库端口暴露到宿主机。

## 一键测试

测试默认使用独立 SQLite 数据库，不需要 MySQL、云服务密钥或已有业务数据。

Windows PowerShell：

```powershell
.\scripts\test.ps1
```

Linux/macOS：

```bash
./scripts/test.sh
```

脚本首次运行会创建 `.venv` 并安装 `requirements.txt`。也可使用完全一致的跨平台 Docker 入口：

```bash
docker build -t food-master:test .
docker run --rm food-master:test python test/run_tests.py
```

报告写入 `test/test_report.md` 和 `test/test_report.json`；任一测试失败时进程返回非 0，流水线立即停止。要额外验证真实 MySQL，请设置 `FOOD_DELIVER_DB_PASSWORD` 及对应的数据库连接环境变量后运行同一命令。

## 本地 Python 启动

本方式需要 Python 3.10 和 MySQL 8.0：

```bash
python -m venv .venv
python -m pip install -r requirements.txt
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS the_food_mas2 DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p --binary-mode the_food_mas2 < data_hex2.sql
python manage.py migrate
python manage.py runserver
```

不要修改 `food_master/settings.py` 写入本机口令。复制 `.env.example` 中的变量到当前终端或使用本机 `.env` 管理工具提供数据库连接信息。

## 测试账号和初始数据

`data_hex2.sql` 仅包含课程演示数据，以下账号不是生产凭据：

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 普通用户 | `user` | `zwj1234567` |
| 骑手 | `rider001` | `hahaha233` |
| 商家 | `testShop` | `test114514` |
| 管理员 | `admin` | `quanju123` |

## CI/CD

向 `main` 或 `master` push 后，`.github/workflows/ci.yml` 自动执行跨平台测试、部署检查、版本化镜像构建与 GHCR 发布，并把同一镜像部署到 Kind Kubernetes 集群做 rollout 和健康检查。测试报告、Pod 日志、资源快照与健康检查响应均作为 GitHub Actions Artifact 保留 30 天。完整部署和回滚方法见 `k8s/README.md`。

镜像同时使用完整 Git 提交 SHA 和分支名作为标签，不使用 `latest`。任何测试、构建、部署或健康检查失败都会阻止后续阶段。

## 最终提交结构

课程 PDF 第 5-6 页要求的 `01_source` 至 `06_defense` 目录映射见 `submission/README.md`。仓库根目录保留 Django 的可运行布局，避免为了打包移动 `manage.py`、Docker 构建上下文和测试入口。

## 已经实现的功能

全部功能已经实现

## 数据库逻辑

### 1. `myapp_user`（用户表）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 用户唯一编号（自增主键） |
| `username` | varchar(20) | 用户名 |
| `password` | varchar(20) | 用户密码 |
| `phone` | varchar(11) | 手机号码 |
| `isDelete` | tinyint(1) | 是否删除（0=正常，1=已删除），默认0 |
| `word` | varchar(50) | 个性签名/个人简介 |
| `usertype` | int | 用户类型（0=普通用户，1=骑手，2=商家），默认0 |

### 2. `myapp_food`（菜品表）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 菜品唯一编号（自增主键） |
| `name` | varchar(20) | 菜品名称 |
| `price` | double | 菜品价格（元） |
| `image` | varchar(100) | 菜品图片路径（相对于static目录） |
| `sale` | int | 售出份数（默认0） |
| `saleperson` | int | 下单次数（默认0） |
| `providor` | varchar(20) | 供应商名称（可为空） |
| `inf` | varchar(200) | 菜品简介/描述信息 |
| `rating` | decimal(2,1) | 菜品评分（范围0.0~5.0，一位小数），默认0.0 |
| `ratenum` | int | 评价人数，默认0 |
| `merchant_id` | bigint | 外键，关联 `myapp_user.id`（创建该菜品的商家），可为空 |

### 3. `myapp_order`（美食订单表）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 订单唯一编号（自增主键） |
| `num` | int | 订单中该菜品的购买数量 |
| `cost` | double | 订单总价（默认0.0） |
| `time` | datetime(6) | 下单时间（自动生成） |
| `comment` | varchar(200) | 订单评论 |
| `address` | varchar(100) | 配送地址 |
| `food_id` | bigint | 外键，关联 `myapp_food.id`（所点菜品） |
| `user_id` | bigint | 外键，关联 `myapp_user.id`（下单用户） |
| `rider_id` | bigint | 外键，关联 `myapp_user.id`（接单骑手），可为空 |
| `pos` | int | 订单状态：0=待分配骑手，1=骑手已接单，2=商家已出餐，3=骑手配送中，4=顾客已取餐，5=顾客已评价 |
| `scoretofood` | decimal(2,1) | 对菜品的评分（0.0~5.0，一位小数），默认0.0 |
| `scoretodeliver` | decimal(2,1) | 对配送服务的评分（0.0~5.0，一位小数），默认0.0 |

### 4. `myapp_hotel`（酒店表）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 酒店唯一编号（自增主键） |
| `name` | varchar(20) | 酒店名称 |
| `addr` | varchar(100) | 酒店位置 |
| `price_clock` | double | 单人间钟点房价格（可为空） |
| `price_day` | double | 单人间日租价格（可为空） |
| `price_double_clock` | double | 双人间钟点房价格（可为空） |
| `price_double_day` | double | 双人间日租价格（可为空） |
| `price_special` | double | 特色房日租价格（可为空） |
| `image` | varchar(100) | 酒店图片路径（相对于static目录） |
| `rating` | decimal(2,1) | 酒店评分（范围0.0~5.0，一位小数），默认0.0 |
| `inf` | varchar(200) | 酒店简介/描述信息 |
| `orders` | int | 订单数量，默认0 |
| `ratenum` | int | 评价人数，默认0 |
| `merchant_id` | bigint | 外键，关联 `myapp_user.id`（创建该酒店的商家），可为空 |

### 5. `myapp_hotelorder`（酒店订单表）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 订单唯一编号（自增主键） |
| `user_id` | bigint | 外键，关联 `myapp_user.id`（下单用户） |
| `hotel_id` | bigint | 外键，关联 `myapp_hotel.id`（所订酒店） |
| `room_type` | varchar(20) | 房型（single_clock/single_day/double_clock/double_day/special_day） |
| `duration` | int | 入住时长（钟点房为小时数，日租房为天数） |
| `checkin_time` | datetime | 预计入住时间 |
| `time` | datetime | 预定时间（自动生成） |
| `cost` | double | 订单总价，默认0.0 |
| `comment` | varchar(200) | 入住评价内容 |
| `score` | decimal(2,1) | 入住评分（0.0~5.0，一位小数），默认0.0 |
| `pos` | int | 订单状态：4=可评价，5=已评价，默认4 |

### 6. `myapp_play`（娱乐场所表）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 娱乐场所唯一编号（自增主键） |
| `name` | varchar(20) | 场所名称 |
| `addr` | varchar(100) | 场所地址 |
| `price` | double | 门票价格（元/张） |
| `start_time` | varchar(50) | 开始营业时间（HH:MM格式），默认09:00 |
| `open_time` | varchar(50) | 运营时长（数字+h格式，如8h、24h），默认24h |
| `image` | varchar(100) | 图片路径（相对于static目录） |
| `rating` | decimal(2,1) | 评分（范围0.0~5.0，一位小数），默认0.0 |
| `ratenum` | int | 评价人数，默认0 |
| `inf` | varchar(200) | 简介/描述信息 |
| `orders` | int | 订单数量，默认0 |
| `merchant_id` | bigint | 外键，关联 `myapp_user.id`（创建该场所的商家），可为空 |

### 7. `myapp_playorder`（娱乐门票订单表）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 订单唯一编号（自增主键） |
| `user_id` | bigint | 外键，关联 `myapp_user.id`（下单用户） |
| `play_id` | bigint | 外键，关联 `myapp_play.id`（所购娱乐场所） |
| `num` | int | 购买票数 |
| `visit_time` | datetime | 预定游玩时间 |
| `time` | datetime | 购买时间（自动生成） |
| `cost` | double | 订单总价，默认0.0 |
| `comment` | varchar(200) | 评价内容 |
| `score` | decimal(2,1) | 游玩评分（0.0~5.0，一位小数），默认0.0 |
| `pos` | int | 订单状态：4=可评价，5=已评价，默认4 |

### 8. `myapp_blog`（博客表，可忽略）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 博客唯一编号（自增主键） |
| `title` | varchar(40) | 博客标题 |
| `content` | longtext | 博客内容 |
| `authorid_id` | bigint | 外键，关联 `myapp_user.id`（作者） |
| `created_at` | datetime(6) | 发布时间（自动生成） |
| `isdeleted` | tinyint(1) | 是否删除（0=正常，1=已删除），默认0 |

### 9. `myapp_comment`（博客评论表，可忽略）

| 字段名 | 类型 | 含义 |
|--------|------|------|
| `id` | bigint | 评论唯一编号（自增主键） |
| `userid` | int | 评论用户ID |
| `content` | longtext | 评论内容 |
| `created_at` | datetime(6) | 评论时间（自动生成） |
| `isdeleted` | tinyint(1) | 是否删除（0=正常，1=已删除），默认0 |
| `blogid_id` | bigint | 外键，关联 `myapp_blog.id`（所属博客） |

### 10. 团购表

### 11. Temp购物车表

### 美食订单状态流转（修改）

```
pos=0(待接单) ──骑手接单──▶ pos=1(骑手已接单) ──商家备餐──▶ pos=2(商家已出餐)──▶ 骑手取餐──▶ pos=3(骑手配送中)
       ──骑手送达──▶ pos=4(顾客已取餐) ──用户评价──▶ pos=5(已评价)
```

| 操作 | 角色 | 状态变化 | URL |
|------|------|----------|-----|
| 接单 | 骑手 | 0→1 | `/rider_accept/` |
| 完成备餐 | 商家 | 1→2 | `/merchant_prepare/` |
| 已送达 | 骑手 | 2→4 | `/rider_deliver/` |
| 评价 | 用户 | 4→5 | `/ordercomment/` |

## 自动化测试

项目在 `test/` 目录下提供了完整的三层自动化测试：

- **单元测试** `test/test_unit.py`：关键类、方法、业务规则与异常分支（价格/房型规则、评价校验、核销码唯一性、密码强度、模型校验、AI 客户端等），全部使用断言判断结果；
- **集成 / API 测试** `test/test_integration_api.py`：模块间调用、数据库访问与对外接口，覆盖每个用例的主成功流程、备选流程和异常流程；
- **端到端测试** `test/test_e2e.py`：从页面/接口入口走完完整业务流程，覆盖美食外卖、购物车、团购、酒店、娱乐、博客、后台管理、AI 助手等全部业务场景；
- **数据库环境检查** `test/test_database_config.py`：校验配置与 `data_hex2.sql` 一致性，并在 MySQL 可达时检查核心表。

一键运行并生成测试报告（总数 / 通过 / 失败 / 失败原因 / 运行环境）：

```powershell
python test/run_tests.py
```

- 默认使用 SQLite 内存测试库，无需配置数据库即可运行；设置 `FOOD_DELIVER_DB_PASSWORD` 后自动切换为 MySQL 验证；
- 任一测试失败时 `run_tests.py` 返回非 0 退出码；镜像和部署 Job 通过 `needs` 依赖测试 Job，**测试失败流水线立即停止发布与部署**；
- 报告输出：`test/test_report.md`（人读）、`test/test_report.json`（机器可读）。详见 `test/README.md`。

## 实现参考

- 可以参考food链路和blog链路的实现方式

### 页面的跳转

- 某个前端设置一个按钮
```
<a href="/hotelorder/?userid={{ user_id }}&hotelid={{ hotel.id }}" class="btn btn-primary">🏨 下单 · 入住</a>
```
class是前端css代码渲染格式，href是跳转链接，userid和hotelid是传递给后端的参数

- 然后`food_master/urls.py`里设置对应的路径和函数
```
path('hotelorder/', views1.hotelorder, name='hotelorder'),
```

- 接着在`hotelorder`函数里获取参数，处理业务逻辑，最后渲染一个页面，例如
```
def hotelorder(request):
    user_id = request.GET.get('userid')
    hotel_id = request.GET.get('hotelid')
    # 处理业务逻辑，获取订单详情等
    foods = Food.objects.all() 获取到所有菜品信息，传递给前端渲染
    food = Food.objects.get(id=food_id) 获取到特定菜品信息，传递给前端渲染
    orders = Order.objects.filter(user=user) 拿到一个集合，传递给前端渲染
    context = {
        'user_id': user_id,
        'hotel_id': hotel_id,
        'foods': foods,
        'food': food,
        'orders': orders,
    }
    return render(request, 'hotel/hotelorder.html', context)
```
context是一个字典，里面是你要传递给前端的数据，前端可以通过`{{ }}`的方式获取到这些数据进行渲染

- 最后在`templates/hotel/hotelorder.html`里设计订单详情页面的前端展示

### 导入类

如果要导入某个关系（某类对象），

- 在`myapp/models.py`里写这个类，比如
```
class Hotel(models.Model):
    name = models.CharField(max_length=20) # 酒店名称
    addr = models.CharField(max_length=100) # 酒店位置
    price_clock = models.FloatField(null=True, blank=True) # 酒店单人间钟点房价格
    # 别的属性自定义
```

- 然后在根目录`food_master`下运行`python manage.py makemigrations`，和`python manage.py migrate`即可

如果要为一个Class追加属性，直接在`myapp/models.py`里这个类追加属性即可，比如为Hotel追加一个评分属性
```
class Hotel(models.Model):
    name = models.CharField(max_length=20) # 酒店名称
    addr = models.CharField(max_length=100) # 酒店位置
    price_clock = models.FloatField(null=True, blank=True) # 酒店单人间钟点房价格
    rating = models.FloatField(default=0.0) # 酒店评分，默认为0.0
    # 别的属性自定义
```
注意要**设定默认值**或者允许null`null=True, blank=True`，否则之前的Hotel对象就无法迁移了

### 最后

这是最后的成品，我们采纳了几乎所有的修改除了以下三点

- 删除了python中用户给美食评分的多余计算更新后分数的代码，已经在sql中采用触发器确保了同步更新
- 没有采用商家在注册时就选择商家名字和类型的方式，一方面一个商家可以搞多个店，另一方面商家名字和类型可以在添加菜品或者酒店的时候设置（而且额外的属性我在搞进去的时候一直报错，自己修改后的代码又很难合并进去，多方考虑决定舍弃）
- 删除了商家交互的很多代码，因为现有的代码已经完全足以模拟用户从下单到评价的全链路（具体：用户下单=商家自动接单--骑手段接单--商家已备餐--骑手已取餐--骑手完成配送--用户评价），故为了从简考虑，删除了这些代码

然后对以下代码进行了修改

- 把“退出登录”的选项放在了个人中心的设置里，而不是放在每个页面的右上角
- 保留先注册再登录的设计，但注册成功后不再直接跳转到首页，而是要跳转到登录页面重新登录
- 修改了下单链路，依然是要骑手先接单商家随后才能备餐，但是顾客下单之后商家能实时看到消息（只是不能点按钮而已），等到骑手接单之后才能点按钮备餐，这给了商家充足的备餐时间

例外加入了以下功能

- **上传图片功能**，商家在创建菜品/商店等时可以从本地上传一张小于2MB的图片
- **购物车功能**，用户可以把想买的菜品加入购物车，最后一起结算下单（仅限于外卖，因为酒店和娱乐场所的订单一般都是单个的，经过反复论证，小组成员一致认为引入购物车会引入不必要的管理复杂度）
- **排序功能**，用户可以根据价格、销量、评分等对菜品/酒店/娱乐场所进行排序
- **AI助手修复**，每个主页面都同步展示AI助手并更新了系统prompt，用户可以和AI跨页面连续对话，AI会基于用户的个人情况和当前平台的状态进行回复，不受刷新页面，切换页面的影响。考虑到平台数据可能过多，我们引入了缓存机制。当然，请在AI 完成对话后再这么操作，在AI尚未生成内容时的操作可能会丢失对话内容
- **前端细节优化**

