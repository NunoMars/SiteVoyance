import json
from channels.generic.websocket import AsyncWebsocketConsumer
from clairvoyance.logic import clairvoyant
from asgiref.sync import sync_to_async


class ClairvoyanteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "clairvoyante_room"
        self.room_group_name = f"clairvoyante_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        input_value = text_data_json["message"]
        # Appeler la fonction clairvoyant de manière asynchrone
        result = await sync_to_async(clairvoyant)(input_value)
        print(result)
        # Envoyer le résultat au groupe de canaux
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "clairvoyante_message", "message": result}
        )

    async def clairvoyante_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))
