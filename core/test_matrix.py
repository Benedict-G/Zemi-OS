import asyncio
from nio import AsyncClient

async def test_login():
    client = AsyncClient("http://localhost:8008", "@zemi2026:localhost")
    
    print("Attempting login...")
    response = await client.login("SecurePass2026")
    
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    
    if hasattr(response, 'access_token'):
        print("✅ Login successful!")
    else:
        print(f"❌ Login failed: {response}")
    
    await client.close()

asyncio.run(test_login())
