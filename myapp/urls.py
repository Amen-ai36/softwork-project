from django.urls import path
from . import views

app_name = "myapp"
urlpatterns = [
    path("ai-chat/", views.ai_chat_view, name="ai_chat"),
]