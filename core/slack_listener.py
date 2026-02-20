import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from cryptography.fernet import Fernet
from slack_memory import log_message, search_memory

def get_token(filename):
    with open(f'/Users/zemi/ZemiV1/vault/master.key', 'rb') as f:
        key = f.read()
    fernet = Fernet(key)
    with open(f'/Users/zemi/ZemiV1/vault/{filename}', 'rb') as ef:
        return fernet.decrypt(ef.read()).decode()

class SlackListener:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.bot_token = get_token('slack.enc')
        self.app_token = get_token('slack_app.enc')
        self.client = WebClient(token=self.bot_token)
        self.bot_id = self.client.auth_test()['user_id']

    def handle_message(self, client, req):
        try:
            client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
            
            payload = req.payload
            event = payload.get('event', {})
            
            # Ignore bot's own messages
            if event.get('bot_id') or event.get('user') == self.bot_id:
                return
            
            message = event.get('text', '').strip()
            user = event.get('user', 'unknown')
            channel = event.get('channel')
            
            if not message or not channel:
                return

            print(f"📥 Slack message from {user}: {message}")

            # Process through orchestrator
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                self.orchestrator.process_command(message, f"@{user}:slack")
            )
            loop.close()

            # Send response back to same channel
            self.client.chat_postMessage(channel=channel, text=str(result))
            # Log to Obsidian memory
            channel_name = channel
            try:
                ch_info = self.client.conversations_info(channel=channel)
                channel_name = ch_info["channel"]["name"]
            except:
                pass
            log_message(channel_name, user, message, str(result))

        except Exception as e:
            print(f"Slack error: {e}")

    def start(self):
        from slack_sdk.socket_mode import SocketModeClient
        socket_client = SocketModeClient(
            app_token=self.app_token,
            web_client=self.client
        )
        socket_client.socket_mode_request_listeners.append(self.handle_message)
        socket_client.connect()
        print("✅ Zemi connected to Slack!")
        from slack_sdk.socket_mode.builtin import SocketModeClient as BuiltinClient
        import time
        while True:
            time.sleep(1)
