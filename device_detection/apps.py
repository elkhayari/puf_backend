from django.apps import AppConfig


class DeviceDetectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'device_detection'

    def ready(self):
        print('ready')
        from .models import TtyDeviceModel  # Import your TtyDeviceModel here
