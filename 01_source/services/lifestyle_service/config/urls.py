from django.urls import path

from services.common import health
from services.lifestyle_service.lifestyle import views

urlpatterns = [
    path("health/live", health.live),
    path("health/ready", health.ready),
    path("health/version", health.version),
    path("hotels", views.hotels),
    path("hotels/<int:hotel_id>", views.hotel_detail),
    path("hotel-orders", views.hotel_orders),
    path("hotel-orders/<int:order_id>", views.hotel_order_detail),
    path("hotel-orders/<int:order_id>/comment", views.hotel_order_comment),
    path("plays", views.plays),
    path("plays/<int:play_id>", views.play_detail),
    path("play-orders", views.play_orders),
    path("play-orders/<int:order_id>", views.play_order_detail),
    path("play-orders/<int:order_id>/comment", views.play_order_comment),
    path("blogs", views.blogs),
    path("blogs/<int:blog_id>", views.blog_detail),
    path("blogs/<int:blog_id>/comments", views.blog_comments),
    path("comments/<int:comment_id>", views.comment_detail),
]
