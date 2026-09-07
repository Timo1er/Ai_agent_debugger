import asyncio
import socket
import websockets

def check_tcp_port(host="127.0.0.1", port=8080):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect((host, port))
        s.close()
        return True, "Port 8080 is OPEN and accepting TCP connections!"
    except Exception as ex:
        return False, f"TCP connect to {host}:{port} failed: {ex}"

async def check_ws():
    tcp_ok, tcp_msg = check_tcp_port()
    print(f"[DIAGNOSTIC] TCP Check: {tcp_msg}")
    if not tcp_ok:
        return

    try:
        ws = await asyncio.wait_for(websockets.connect("ws://127.0.0.1:8080"), timeout=2.0)
        print("[DIAGNOSTIC] WebSocket handshake SUCCESSFUL!")
        await ws.close()
    except Exception as ex:
        print(f"[DIAGNOSTIC] WebSocket handshake FAILED: {ex}")

asyncio.run(check_ws())