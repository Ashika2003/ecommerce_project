import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderNotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for order notifications"""
    
    async def connect(self):
        """Connect to WebSocket"""
        # Get the user from the scope
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            # Reject the connection if user is not authenticated
            await self.close()
            return
        
        # Create a user-specific group
        self.group_name = f"user_{self.user.id}"
        
        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Disconnect from WebSocket"""
        # Leave the group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        # We don't expect to receive messages, but handle it anyway
        pass
    
    async def order_notification(self, event):
        """Send order notification to WebSocket"""
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))