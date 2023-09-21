import json
from channels.generic.websocket import AsyncWebsocketConsumer


class HeatmapConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('Heatmap Consumer Connected')
        await self.channel_layer.group_add("heatmap_group", self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # This can be expanded as per your needs
        pass

    async def heatmap_update(self, event):
        print('heatmap update')
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
