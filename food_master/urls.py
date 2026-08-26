"""food_master URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from myapp import admin_views, health, service_views, views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/live/", health.live, name="health_live"),
    path("health/ready/", health.ready, name="health_ready"),
    path("health/version/", health.version, name="health_version"),
    # ********** Begin **********#
    path("", views.index),
    path("index/", views.index),
    path("account/login/", views.login),
    path("account/register/", views.register),
    path("logout/", views.logout_view, name="logout"),
    path("food/", views.food),
    path("foodsend/", views.foodsend, name="foodsend"),
    path(
        "merchant/food/action/", views.merchant_food_action, name="merchant_food_action"
    ),
    path("space/", views.space, name="space"),
    path("fooddetails/", views.fooddetails, name="fooddetails"),
    path("foodorder/", views.foodorder, name="foodorder"),
    path("groupbuyorder/", views.groupbuyorder, name="groupbuyorder"),
    path("groupbuy/redeem/", views.groupbuy_redeem, name="groupbuy_redeem"),
    path("orderpos/", views.orderpos, name="orderpos"),
    path("ordercomment/", views.ordercomment, name="ordercomment"),
    path("cart/update/<int:tempid>/", views.update_cart_item, name="update_cart_item"),
    path("cart/delete/<int:tempid>/", views.delete_cart_item, name="delete_cart_item"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("blog/", views.blog, name="blog"),
    path("blogsend/", views.blogsend, name="blogsend"),
    path("blogsdetails/", views.blogsdetails, name="blogsdetails"),
    path("blogcomment/", views.blogcomment, name="blogcomment"),
    path("blog/delete/", views.delete_blog, name="delete_blog"),
    path("blogcomment/delete/", views.delete_comment, name="delete_comment"),
    path("play/", service_views.play, name="play"),
    path("hotel/", service_views.hotel, name="hotel"),
    path("hotelsend/", service_views.hotelsend, name="hotelsend"),
    path("hoteldetails/", service_views.hoteldetails, name="hoteldetails"),
    path("hotelorder/", service_views.hotelorder, name="hotelorder"),
    path("hotelcomment/", service_views.hotelcomment, name="hotelcomment"),
    path("hotelorderpos/", service_views.hotelorderpos, name="hotelorderpos"),
    path("playsend/", service_views.playsend, name="playsend"),
    path("playdetails/", service_views.playdetails, name="playdetails"),
    path("playorder/", service_views.playorder, name="playorder"),
    path("playcomment/", service_views.playcomment, name="playcomment"),
    path("playorderpos/", service_views.playorderpos, name="playorderpos"),
    path("rider/", service_views.rider_orders, name="rider_orders"),
    path("rider_accept/", service_views.rider_accept, name="rider_accept"),
    path("rider_get/", service_views.rider_get, name="rider_get"),
    path("rider_deliver/", service_views.rider_deliver, name="rider_deliver"),
    path("merchant_prepare/", service_views.merchant_prepare, name="merchant_prepare"),
    path("manage/", admin_views.admin_dashboard, name="app_admin_dashboard"),
    path(
        "manage/users/action/",
        admin_views.admin_user_action,
        name="app_admin_user_action",
    ),
    path(
        "manage/orders/action/",
        admin_views.admin_order_action,
        name="app_admin_order_action",
    ),
    path(
        "manage/blogs/action/",
        admin_views.admin_blog_action,
        name="app_admin_blog_action",
    ),
    path("manage/logout/", admin_views.admin_logout, name="app_admin_logout"),
    path("", include("myapp.urls")),
]
