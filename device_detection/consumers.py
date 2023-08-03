import json
import threading
from channels.generic.websocket import AsyncWebsocketConsumer
import pyudev
from asgiref.sync import async_to_sync
from django.apps import apps


class DeviceChangeConsumer(AsyncWebsocketConsumer):

    device_group_name = "state-devices"
    monitor_thread = None
    monitor_running = False

    async def connect(self):
        print('connected')
        await self.channel_layer.group_add(self.device_group_name, self.channel_name)
        await self.accept()

        # Start the thread to listen for tty devices
        self.start_device_monitor()

    async def disconnect(self, close_code):
        print('disconnect with code:', close_code)
        if self.monitor_thread:
            self.monitor_running = False
            self.monitor_thread.join()

        await self.channel_layer.group_discard(self.device_group_name, self.channel_name)

    def start_device_monitor(self):
        def monitor_thread_func():
            context = pyudev.Context()
            monitor = pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem='tty')

            self.monitor_running = True
            while self.monitor_running:
                try:
                    device = monitor.poll(timeout=1)
                    if device:
                        # Process the device change
                        action = device.action
                        device_info = {
                            'action': action,
                            'device_node': device.device_node,
                        }
                        print(device_info)

                        TtyDeviceModel = apps.get_model(
                            'device_detection', 'TtyDeviceModel')

                        if action == 'add':
                            try:
                                tty_device = TtyDeviceModel.objects.get(
                                    device_port=device.device_node)
                                if tty_device:
                                    tty_device.delete()
                            except TtyDeviceModel.DoesNotExist:
                                pass
                            finally:
                                TtyDeviceModel.objects.create(
                                    device_port=device.device_node,
                                    is_connected=False
                                )
                                self.notify_device_change(device_info)

                        else:
                            TtyDeviceModel.objects.filter(
                                device_port=device.device_node).delete()
                            self.notify_device_change(device_info)

                        # Notify the client

                except Exception as e:
                    print(f"Error in device monitoring: {e}")
                    break

        # Start the thread
        self.monitor_thread = threading.Thread(target=monitor_thread_func)
        self.monitor_thread.start()

    def notify_device_change(self, device_info):
        async def send_notification():
            await self.channel_layer.group_send(self.device_group_name, {
                'type': 'send_device_change',
                'message': device_info
            })

        # Run the send_notification coroutine in the event loop
        async_to_sync(send_notification)()
#

    async def send_device_change(self, event):
        message = event['message']
        type = event['type']
        print('device_change')
        await self.send(text_data=json.dumps({'type': type, 'message': message}))
