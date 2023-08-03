from django.urls import path
from .views import ConnectedDevicesAPI, InsertedDevicesAPI
from . import views

urlpatterns = [
    # Other URL patterns
    path('insertDevice/', InsertedDevicesAPI.as_view(),
         name='insert_device'),
    path('connectedDevice/', ConnectedDevicesAPI.as_view(),
         name='connected_device'),
    path('connectDeviceByPort/', views.connect_device_by_port)
]
