from django.urls import re_path
from . import consumers
from channels.routing import ProtocolTypeRouter, URLRouter


heatmap_websocket_urlpatterns = [
    re_path('ws/heatmap/', consumers.HeatmapConsumer.as_asgi()),
]

channel_routing = {
    'websocket': consumers.HeatmapConsumer.as_asgi(),
}
