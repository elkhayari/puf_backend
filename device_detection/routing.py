from django.urls import re_path, path
from .consumers import DeviceChangeConsumer

websocket_urlpatterns = [
    re_path('ws/devices/', DeviceChangeConsumer.as_asgi()),
]


channel_routing = {
    'websocket': DeviceChangeConsumer.as_asgi(),
}
