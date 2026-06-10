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
from myapp import admin_views, views, views1

urlpatterns = [
    path('admin/', admin.site.urls),
#********** Begin **********#
    path("", views.index),
    path("index/", views.index),
    path("account/login/", views.login),
    path("account/register/", views.register),
    path("food/", views.food),
    path('foodsend/', views.foodsend, name='foodsend'),
    path('space/', views.space, name='space'),
    path('fooddetails/', views.fooddetails, name='fooddetails'),
    path('foodorder/', views.foodorder, name='foodorder'),
    path('groupbuyorder/', views.groupbuyorder, name='groupbuyorder'),
    path('groupbuy/redeem/', views.groupbuy_redeem, name='groupbuy_redeem'),
    path('orderpos/', views.orderpos, name='orderpos'),
    path('ordercomment/', views.ordercomment, name='ordercomment'),
    path('cart/update/<int:tempid>/', views.update_cart_item, name='update_cart_item'),
    path('cart/delete/<int:tempid>/', views.delete_cart_item, name='delete_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('blog/', views.blog, name='blog'),
    path('blogsend/', views.blogsend, name='blogsend'),
    path('blogsdetails/', views.blogsdetails, name='blogsdetails'),
    path('blogcomment/', views.blogcomment, name='blogcomment'),
    path('blog/delete/', views.delete_blog, name='delete_blog'),
    path('blogcomment/delete/', views.delete_comment, name='delete_comment'),
    path('play/', views1.play, name='play'),
    path('hotel/', views1.hotel, name='hotel'),
    path('hotelsend/', views1.hotelsend, name='hotelsend'),
    path('hoteldetails/', views1.hoteldetails, name='hoteldetails'),
    path('hotelorder/', views1.hotelorder, name='hotelorder'),
    path('hotelcomment/', views1.hotelcomment, name='hotelcomment'),
    path('hotelorderpos/', views1.hotelorderpos, name='hotelorderpos'),
    path('play/', views1.play, name='play'),
    path('playsend/', views1.playsend, name='playsend'),
    path('playdetails/', views1.playdetails, name='playdetails'),
    path('playorder/', views1.playorder, name='playorder'),
    path('playcomment/', views1.playcomment, name='playcomment'),
    path('playorderpos/', views1.playorderpos, name='playorderpos'),
    path('rider/', views1.rider_orders, name='rider_orders'),
    path('rider_accept/', views1.rider_accept, name='rider_accept'),
    path('rider_get/', views1.rider_get, name='rider_get'),
    path('rider_deliver/', views1.rider_deliver, name='rider_deliver'),
    path('merchant_prepare/', views1.merchant_prepare, name='merchant_prepare'),
    path('manage/', admin_views.admin_dashboard, name='app_admin_dashboard'),
    path('manage/users/action/', admin_views.admin_user_action, name='app_admin_user_action'),
    path('manage/orders/action/', admin_views.admin_order_action, name='app_admin_order_action'),
    path('manage/blogs/action/', admin_views.admin_blog_action, name='app_admin_blog_action'),
    path('manage/logout/', admin_views.admin_logout, name='app_admin_logout'),
    path('', include('myapp.urls')),
]
