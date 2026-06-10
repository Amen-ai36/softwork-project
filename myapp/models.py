from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

USER_TYPE_CHOICES = (
    (0, '普通用户'),
    (1, '骑手'),
    (2, '商家'),
    (3, '管理员'),
)

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20) # 用户名称
    password = models.CharField(max_length=20) # 用户密码
    phone = models.CharField(max_length=11) # 用户手机号
    word = models.CharField(max_length=50, default="") # 用户个性签名
    isDelete = models.BooleanField(default=False) # 逻辑删除
    usertype = models.IntegerField(default=0, choices=USER_TYPE_CHOICES) # 用户类型，0-普通用户，1-骑手，2-商家

class Food(models.Model):
    name = models.CharField(max_length=20) # 食物名称
    price = models.FloatField() # 食物价格
    image = models.CharField(max_length=100) # 食物图片地址
    sale = models.IntegerField(default=0) # 销量（售出份数）
    saleperson = models.IntegerField(default=0) # （下单次数）
    providor = models.CharField(max_length=20) # 食物提供商
    ratenum = models.IntegerField(default=0) # 评分人数
    rating = models.DecimalField(
        max_digits=2,          # 总位数：整数1位 + 小数1位 = 2位
        decimal_places=1,      # 小数位数：1位
        default=0.0,           # 默认值
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    ) # 食物评分，0.0-5.0之间，保留1位小数
    inf = models.CharField(max_length=200, default="") # 食物简介
    merchant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='foods') # 创建商家

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 订单所属用户
    food = models.ForeignKey(Food, on_delete=models.CASCADE) # 订单所属食物
    rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rider_orders') # 接单骑手
    num = models.IntegerField() # 订单中食物的数量
    cost = models.FloatField(default=0.0) # 订单总价
    time = models.DateTimeField(auto_now_add=True) # 订单创建时间
    address = models.CharField(max_length=100, default="") # 订单配送地址
    comment = models.CharField(max_length=200, default="") # 订单评价
    pos = models.IntegerField(default=0) # 0-待分配骑手，1-骑手已分配 2-商家已出餐 3-骑手配送中 4-顾客已取餐 5-顾客已评价
    is_abnormal = models.BooleanField(default=False) # 管理员标记的异常订单
    scoretofood = models.DecimalField(
        max_digits=2,          # 总位数：整数1位 + 小数1位 = 2位
        decimal_places=1,      # 小数位数：1位
        default=0.0,           # 默认值
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    ) # 食物评分，0.0-5.0之间，保留1位小数
    scoretodeliver = models.DecimalField(
        max_digits=2,          # 总位数：整数1位 + 小数1位 = 2位
        decimal_places=1,      # 小数位数：1位
        default=0.0,           # 默认值
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    ) # 配送评分，0.0-5.0之间，保留1位小数

class GroupBuyCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 团购券所属用户
    food = models.ForeignKey(Food, on_delete=models.CASCADE) # 团购对应美食
    num = models.IntegerField() # 购买数量
    cost = models.FloatField(default=0.0) # 团购总价
    code = models.CharField(max_length=20, unique=True) # 到店核销码
    status = models.IntegerField(default=0) # 0-待使用，1-已使用，2-已取消
    time = models.DateTimeField(auto_now_add=True) # 购买时间
    used_at = models.DateTimeField(null=True, blank=True) # 核销时间

class Blog(models.Model):
    title = models.CharField(max_length=40) # 博客标题
    content = models.TextField() # 博客内容
    authorid = models.ForeignKey(User, on_delete=models.CASCADE) # 订单所属用户
    created_at = models.DateTimeField(auto_now_add=True) # 博客创建时间
    isdeleted = models.BooleanField(default=False) # 逻辑删除

class Comment(models.Model):
    blogid = models.ForeignKey(Blog, on_delete=models.CASCADE) # 评论所属博客
    userid = models.IntegerField() # 评论所属用户
    content = models.TextField() # 评论内容
    created_at = models.DateTimeField(auto_now_add=True) # 评论创建时间
    isdeleted = models.BooleanField(default=False) # 逻辑删除

class Hotel(models.Model):
    name = models.CharField(max_length=20) # 酒店名称
    addr = models.CharField(max_length=100) # 酒店位置
    price_clock = models.FloatField(null=True, blank=True) # 酒店单人间钟点房价格
    price_day = models.FloatField(null=True, blank=True) # 酒店单人间日租价格
    price_double_clock = models.FloatField(null=True, blank=True) # 酒店双人间钟点房价格
    price_double_day = models.FloatField(null=True, blank=True) # 酒店双人间日租价格
    price_special = models.FloatField(null=True, blank=True) # 酒店特色房日租价格
    image = models.CharField(max_length=100) # 酒店图片地址
    rating = models.DecimalField(
        max_digits=2,          # 总位数：整数1位 + 小数1位 = 2位
        decimal_places=1,      # 小数位数：1位
        default=0.0,           # 默认值
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    ) # 酒店评分，0.0-5.0之间，保留1位小数
    inf = models.CharField(max_length=200, default="") # 酒店简介
    orders = models.IntegerField(default=0) # 订单数
    ratenum = models.IntegerField(default=0) # 评分人数
    merchant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hotels') # 创建商家

class HotelOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 订单所属用户
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE) # 订单所属酒店
    room_type = models.CharField(max_length=20) # 房型
    duration = models.IntegerField() # 入住时长（钟点房为小时，日租房为天数）
    checkin_time = models.DateTimeField() # 预计入住时间
    time = models.DateTimeField(auto_now_add=True) # 预定时间
    cost = models.FloatField(default=0.0) # 订单总价
    comment = models.CharField(max_length=200, default="") # 入住评价内容
    score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    ) # 入住评分，0.0-5.0之间，保留1位小数
    pos = models.IntegerField(default=4) # 4-可评价，5-已评价

class Play(models.Model):
    name = models.CharField(max_length=20) # 娱乐场所名称
    addr = models.CharField(max_length=100) # 地址
    price = models.FloatField() # 门票价格
    start_time = models.CharField(max_length=50, default='09:00') # 开始营业时间
    open_time = models.CharField(max_length=50, default='24h') # 运营时间
    image = models.CharField(max_length=100) # 图片地址
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    ) # 评分，0.0-5.0之间，保留1位小数
    ratenum = models.IntegerField(default=0) # 评分人数
    inf = models.CharField(max_length=200, default="") # 简介
    orders = models.IntegerField(default=0) # 订单数
    merchant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='plays') # 创建商家

class PlayOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 订单所属用户
    play = models.ForeignKey(Play, on_delete=models.CASCADE) # 订单所属娱乐场所
    num = models.IntegerField() # 购买票数
    visit_time = models.DateTimeField() # 预定游玩时间
    time = models.DateTimeField(auto_now_add=True) # 购买时间
    cost = models.FloatField(default=0.0) # 订单总价
    comment = models.CharField(max_length=200, default="") # 评价内容
    score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    ) # 评分，0.0-5.0之间，保留1位小数
    pos = models.IntegerField(default=4) # 4-可评价，5-已评价

class Temp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 订单所属用户
    food = models.ForeignKey(Food, on_delete=models.CASCADE) # 订单所属食物
    num = models.IntegerField() # 订单中食物的数量
    cost = models.FloatField(default=0.0) # 订单单价
    address = models.CharField(max_length=100, default="") # 订单配送地址
    pos = models.IntegerField(default=0) # 0-待定，1-已删除，2-已提交
