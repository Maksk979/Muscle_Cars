from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/like/', consumers.LikeConsumer.as_asgi()),
]