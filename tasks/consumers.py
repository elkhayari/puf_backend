import json
from channels.generic.websocket import AsyncWebsocketConsumer


class HeatmapConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # This can be expanded as per your needs
        pass

    async def heatmap_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
