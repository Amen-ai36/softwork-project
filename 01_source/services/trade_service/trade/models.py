from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Food(models.Model):
    name = models.CharField(max_length=20)
    price = models.FloatField()
    image = models.CharField(max_length=200, default="", blank=True)
    sale = models.IntegerField(default=0)
    saleperson = models.IntegerField(default=0)
    providor = models.CharField(max_length=40)
    ratenum = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    inf = models.CharField(max_length=200, default="", blank=True)
    merchant_id = models.BigIntegerField(db_index=True)
    is_off_shelf = models.BooleanField(default=False)
    is_sold_out = models.BooleanField(default=False)

    class Meta:
        db_table = "foods"


class Order(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    rider_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="orders")
    num = models.PositiveIntegerField()
    cost = models.FloatField(default=0.0)
    time = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=100, default="")
    comment = models.CharField(max_length=200, default="", blank=True)
    pos = models.IntegerField(default=0)
    is_abnormal = models.BooleanField(default=False)
    scoretofood = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    scoretodeliver = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )

    class Meta:
        db_table = "orders"


class GroupBuyCoupon(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="coupons")
    num = models.PositiveIntegerField()
    cost = models.FloatField(default=0.0)
    code = models.CharField(max_length=20, unique=True)
    status = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "group_buy_coupons"


class CartItem(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="cart_items")
    num = models.PositiveIntegerField()
    cost = models.FloatField(default=0.0)
    address = models.CharField(max_length=100, default="")

    class Meta:
        db_table = "cart_items"
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "food"], name="unique_user_food_cart_item"
            )
        ]
