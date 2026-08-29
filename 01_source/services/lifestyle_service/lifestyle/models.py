from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

RATING_VALIDATORS = [MinValueValidator(0.0), MaxValueValidator(5.0)]


class Hotel(models.Model):
    name = models.CharField(max_length=40)
    addr = models.CharField(max_length=100)
    price_clock = models.FloatField(null=True, blank=True)
    price_day = models.FloatField(null=True, blank=True)
    price_double_clock = models.FloatField(null=True, blank=True)
    price_double_day = models.FloatField(null=True, blank=True)
    price_special = models.FloatField(null=True, blank=True)
    image = models.CharField(max_length=200, default="", blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    inf = models.CharField(max_length=200, default="", blank=True)
    orders = models.IntegerField(default=0)
    ratenum = models.IntegerField(default=0)
    merchant_id = models.BigIntegerField(db_index=True)

    class Meta:
        db_table = "hotels"


class HotelOrder(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="bookings")
    room_type = models.CharField(max_length=20)
    duration = models.PositiveIntegerField()
    checkin_time = models.DateTimeField()
    time = models.DateTimeField(auto_now_add=True)
    cost = models.FloatField(default=0.0)
    comment = models.CharField(max_length=200, default="", blank=True)
    score = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0, validators=RATING_VALIDATORS
    )
    pos = models.IntegerField(default=4)

    class Meta:
        db_table = "hotel_orders"


class Play(models.Model):
    name = models.CharField(max_length=40)
    addr = models.CharField(max_length=100)
    price = models.FloatField()
    start_time = models.CharField(max_length=50, default="09:00")
    open_time = models.CharField(max_length=50, default="24h")
    image = models.CharField(max_length=200, default="", blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    ratenum = models.IntegerField(default=0)
    inf = models.CharField(max_length=200, default="", blank=True)
    orders = models.IntegerField(default=0)
    merchant_id = models.BigIntegerField(db_index=True)

    class Meta:
        db_table = "plays"


class PlayOrder(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name="bookings")
    num = models.PositiveIntegerField()
    visit_time = models.DateTimeField()
    time = models.DateTimeField(auto_now_add=True)
    cost = models.FloatField(default=0.0)
    comment = models.CharField(max_length=200, default="", blank=True)
    score = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0, validators=RATING_VALIDATORS
    )
    pos = models.IntegerField(default=4)

    class Meta:
        db_table = "play_orders"


class Blog(models.Model):
    title = models.CharField(max_length=40)
    content = models.TextField()
    author_id = models.BigIntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "blogs"


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user_id = models.BigIntegerField(db_index=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "comments"
