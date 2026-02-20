import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import ZemiOrchestrator as Orchestrator
from slack_listener import SlackListener

async def main():
    print("🚀 Starting Zemi...")
    orchestrator = Orchestrator()
    print("✅ Orchestrator ready")
    print("✅ Connecting to Slack...")
    slack = SlackListener(orchestrator)
    slack.start()

if __name__ == "__main__":
    asyncio.run(main())
