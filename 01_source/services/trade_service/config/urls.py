from django.urls import path

from services.common import health
from services.trade_service.trade import views

urlpatterns = [
    path("health/live", health.live),
    path("health/ready", health.ready),
    path("health/version", health.version),
    path("foods", views.foods),
    path("foods/<int:food_id>", views.food_detail),
    path("foods/<int:food_id>/status", views.food_status),
    path("orders", views.orders),
    path("orders/<int:order_id>", views.order_detail),
    path("orders/<int:order_id>/comment", views.order_comment),
    path("orders/<int:order_id>/accept", views.order_accept),
    path("orders/<int:order_id>/prepare", views.order_prepare),
    path("orders/<int:order_id>/pickup", views.order_pickup),
    path("orders/<int:order_id>/deliver", views.order_deliver),
    path("cart", views.cart),
    path("cart/<int:item_id>", views.cart_item),
    path("cart/checkout", views.cart_checkout),
    path("groupbuy", views.groupbuy),
    path("groupbuy/redeem", views.groupbuy_redeem),
    path("rider/orders", views.rider_orders),
]
