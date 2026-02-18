"""
Zemi Main - Connects Orchestrator + Matrix
"""

import asyncio
from orchestrator import ZemiOrchestrator
from matrix_listener import MatrixListener

async def main():
    print("="*60)
    print("🤖 ZEMI V1 - Starting System")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = ZemiOrchestrator()
    
    # Initialize Matrix listener
    matrix = MatrixListener(
        homeserver="http://100.111.133.70:8008",
        user_id="@zemi2026:localhost",
        password="SecurePass2026"
    )
    
    # Connect them
    matrix.set_orchestrator(orchestrator)
    
    print("\n✅ All systems initialized")
    print("📱 Connect via Element app to send commands")
    print("🔗 Matrix server: http://100.111.133.70:8008")
    print("\n")
    
    # Start listening
    await matrix.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Zemi shutting down...")
