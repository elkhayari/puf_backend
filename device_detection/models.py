from django.db import models
from django.utils import timezone
from django.utils.timesince import timesince


class TtyDeviceModel(models.Model):
    device_port = models.CharField(
        max_length=255, blank=True, null=True, unique=True)
    is_connected = models.BooleanField(default=False, blank=True, null=True)
    is_busy = models.BooleanField(default=False, blank=True, null=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.CharField(max_length=100, blank=True, null=True)
    device_label = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    connected_since = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.device_port

    def get_connected_since_display(self):
        if self.connected_since:
            return timesince(self.connected_since) + ' ago'
        return ''

    def save(self, *args, **kwargs):
        if self.is_connected and not self.connected_since:
            self.connected_since = timezone.now()
        super().save(*args, **kwargs)
