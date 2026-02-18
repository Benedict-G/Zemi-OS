"""
Zemi Matrix Listener
Connects to Matrix server and listens for commands
"""

import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText, InviteEvent

class MatrixListener:
    def __init__(self, homeserver, user_id, password, room_id=None):
        self.homeserver = homeserver
        self.user_id = user_id
        self.password = password
        self.room_id = room_id
        self.client = AsyncClient(homeserver, user_id)
        self.orchestrator = None
        
        self.client.add_event_callback(self.message_callback, RoomMessageText)
        self.client.add_event_callback(self.invite_callback, InviteEvent)
    
    def set_orchestrator(self, orchestrator):
        self.orchestrator = orchestrator
    
    async def invite_callback(self, room, event):
        print(f"📨 Invited to room: {room.room_id}")
        await self.client.join(room.room_id)
        print(f"✅ Joined room: {room.room_id}")
    
    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        if event.sender == self.user_id:
            return
        
        if self.room_id and room.room_id != self.room_id:
            return
        
        message = event.body
        sender = event.sender
        
        print(f"\n📱 Matrix message from {sender}: {message}")
        
        if self.orchestrator:
            result = await self.orchestrator.process_command(message, sender)
            await self.send_message(room.room_id, result)
        else:
            await self.send_message(room.room_id, "⚠️ Orchestrator not connected")
    
    async def send_message(self, room_id, message):
        try:
            await self.client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message
                }
            )
            print(f"✉️ Sent to Matrix: {message[:100]}...")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
    
    async def start(self):
        print(f"🔗 Connecting to Matrix: {self.homeserver}")
        
        login_response = await self.client.login(self.password)
        
        if not hasattr(login_response, 'access_token'):
            print(f"❌ Login failed: {login_response}")
            return
        
        print(f"✅ Logged in as {self.user_id}")
        
        print("🔄 Performing initial sync...")
        sync_response = await self.client.sync(timeout=30000)
        print(f"✅ Initial sync complete - {len(sync_response.rooms.join)} rooms joined")
        
        print("👂 Listening for messages...")

         # Manual polling loop
        while True:
            sync_response = await self.client.sync(timeout=30000)            
            print(f"🔍 Sync: {len(sync_response.rooms.join)} rooms")
            # Callbacks handle messages automatically
            await asyncio.sleep(1)

async def stop(self):
    await self.client.close()
