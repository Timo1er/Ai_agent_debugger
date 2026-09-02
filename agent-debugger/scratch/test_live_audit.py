import asyncio
from debugger_client.unity_client import UnityDebuggerClient

async def test():
    client = UnityDebuggerClient("127.0.0.1", 8080)
    connected = await client.connect()
    if not connected:
        print("Could not connect to Unity (Play mode not active?)")
        return
    print("Connected to Unity!")
    
    # 1. Audit gameplay bugs
    bugs = await client.audit_gameplay_bugs()
    print(f"\nGameplay bugs found ({len(bugs)}):")
    for b in bugs:
        print(f" - [{b.get('severity')}] {b.get('title')}: {b.get('description')}")

    # 2. Tunneling events
    tunnels = await client.get_tunneling_events()
    print(f"\nTunneling events ({len(tunnels)}):")
    for t in tunnels:
        print(f" - {t}")

    await client.disconnect()

asyncio.run(test())