from channels.routing import ProtocolTypeRouter, URLRouter
from device_detection.routing import websocket_urlpatterns
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from device_detection.consumers import DeviceNotificationConsumer

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AllowedHostsOriginValidator(
            URLRouter([
                path('', DeviceNotificationConsumer)])
        ),
    }
)
