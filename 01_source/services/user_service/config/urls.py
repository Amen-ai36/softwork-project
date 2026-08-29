from django.urls import path

from services.common import health
from services.user_service.users import views

urlpatterns = [
    path("health/live", health.live),
    path("health/ready", health.ready),
    path("health/version", health.version),
    path("register", views.register),
    path("login", views.login),
    path("logout", views.logout),
    path("users/<int:user_id>", views.user_detail),
    path("users/<int:user_id>/profile", views.user_profile),
    path("users/<int:user_id>/status", views.user_status),
    path("users/<int:user_id>/role", views.user_role),
    path("internal/users", views.internal_users),
]
