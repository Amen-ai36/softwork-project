from django.contrib import admin

from .models import Blog, Comment, Food, GroupBuyCoupon, Hotel, HotelOrder, Order, Play, PlayOrder, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'phone', 'usertype', 'isDelete')
    list_filter = ('usertype', 'isDelete')
    search_fields = ('username', 'phone')


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'providor', 'merchant', 'rating', 'sale')
    search_fields = ('name', 'providor')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'food', 'rider', 'num', 'cost', 'pos', 'time')
    list_filter = ('pos',)
    search_fields = ('user__username', 'food__name', 'address')


@admin.register(GroupBuyCoupon)
class GroupBuyCouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'food', 'num', 'cost', 'code', 'status', 'time', 'used_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'food__name', 'code')


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'addr', 'merchant', 'rating', 'orders')
    search_fields = ('name', 'addr')


@admin.register(HotelOrder)
class HotelOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'hotel', 'room_type', 'cost', 'pos', 'time')
    list_filter = ('pos', 'room_type')


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'addr', 'price', 'merchant', 'rating', 'orders')
    search_fields = ('name', 'addr')


@admin.register(PlayOrder)
class PlayOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'play', 'num', 'cost', 'pos', 'time')
    list_filter = ('pos',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'authorid', 'created_at', 'isdeleted')
    list_filter = ('isdeleted',)
    search_fields = ('title', 'authorid__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'blogid', 'userid', 'created_at', 'isdeleted')
    list_filter = ('isdeleted',)

# Register your models here.
