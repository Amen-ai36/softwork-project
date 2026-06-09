# 功能介绍

## 首先项目运行方式
1. 安装依赖：
pip install -r requirements.txt

2. 安装数据库：
先创建数据库
  mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS the_food_master DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
然后导入sql脚本：
导入SQL脚本（记得用cmd执行，如果不行尝试重新下载，并且不要用vscode打开该sql语句）
  mysql -u root -p --binary-mode the_food_master < data_hex2.sql

3. 设置好你的settings.py里数据库的用户名和密码

这个根目录`food_master`下运行`python manage.py runserver`即可

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

