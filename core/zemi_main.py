import asyncio
from orchestrator import ZemiOrchestrator as Orchestrator
from slack_listener import SlackListener

async def main():
    print("🚀 Starting Zemi...")
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    print("✅ Orchestrator ready")
    print("✅ Connecting to Slack...")
    
    # Start Slack listener
    slack = SlackListener(orchestrator)
    slack.start()

if __name__ == "__main__":
    asyncio.run(main())
