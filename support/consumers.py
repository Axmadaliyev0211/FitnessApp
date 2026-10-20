import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SupportMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class SupportChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = f"support_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Oldingi xabarlarni yuborish
        messages = await self.get_messages()
        await self.send(text_data=json.dumps({
            "type": "history",
            "messages": messages
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        if not message:
            return

        # Xabarni saqlash
        msg = await self.save_message(message)

        # Foydalanuvchiga yuborish
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"]
        }))

    @database_sync_to_async
    def save_message(self, message):
        msg = SupportMessage.objects.create(
            user=self.user,
            message=message,
            is_from_user=True
        )
        return {
            "id": str(msg.id),
            "message": msg.message,
            "is_from_user": msg.is_from_user,
            "created_at": msg.created_at.isoformat()
        }

    @database_sync_to_async
    def get_messages(self):
        messages = SupportMessage.objects.filter(user=self.user).order_by('created_at')[:50]
        return [
            {
                "id": str(m.id),
                "message": m.message,
                "is_from_user": m.is_from_user,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]