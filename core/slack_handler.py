from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from cryptography.fernet import Fernet
import threading

def get_slack_token():
    with open('/Users/zemi/ZemiV1/vault/master.key', 'rb') as f:
        key = f.read()
    f = Fernet(key)
    with open('/Users/zemi/ZemiV1/vault/slack.enc', 'rb') as ef:
        return f.decrypt(ef.read()).decode()

class SlackHandler:
    def __init__(self, orchestrator):
        self.token = get_slack_token()
        self.client = WebClient(token=self.token)
        self.orchestrator = orchestrator

    def send_message(self, channel, text):
        self.client.chat_postMessage(channel=channel, text=text)

    def get_channels(self):
        result = self.client.conversations_list()
        return [c['name'] for c in result['channels']]
