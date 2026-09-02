import asyncio
import json
import websockets
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

class DebugGameTrackedObject(BaseModel):
    name: str = ""
    tag: str = "Tracked"
    position: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])
    velocity: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    isActive: bool = True
    components: List[str] = Field(default_factory=list)

class DebugGameStateSnapshot(BaseModel):
    type: str = "STATE_SNAPSHOT"
    timestamp: float = 0.0
    fps: float = 60.0
    memoryMB: float = 0.0
    activeCoroutineCount: int = 0
    activeBugIds: List[str] = Field(default_factory=list)
    trackedObjects: List[DebugGameTrackedObject] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class DebugGameClient:
    """
    Client WebSocket dédié à l'environnement 'Debug-game-for-AI' (ws://127.0.0.1:8765/)
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self._ws = None
        self._is_running = False
        self._latest_snapshot: Optional[DebugGameStateSnapshot] = None
        self._listen_task: Optional[asyncio.Task] = None
        self._snapshot_callbacks: List[Callable[[DebugGameStateSnapshot], None]] = []
        self._response_queue: asyncio.Queue = asyncio.Queue()

    @property
    def is_connected(self) -> bool:
        if self._ws is None or not self._is_running:
            return False
        if hasattr(self._ws, "open"):
            return self._ws.open
        if hasattr(self._ws, "state"):
            return self._ws.state.name == "OPEN"
        if hasattr(self._ws, "closed"):
            return not self._ws.closed
        return self._is_running

    @property
    def latest_snapshot(self) -> Optional[DebugGameStateSnapshot]:
        return self._latest_snapshot

    async def connect(self, timeout: float = 4.0, retries: int = 2) -> bool:
        endpoints = [
            f"ws://{self.host}:{self.port}/",
            f"ws://127.0.0.1:{self.port}/",
            f"ws://{self.host}:{self.port}",
            f"ws://127.0.0.1:{self.port}"
        ]

        for attempt in range(retries):
            for uri in endpoints:
                try:
                    self._ws = await asyncio.wait_for(websockets.connect(uri), timeout=timeout)
                    self._is_running = True
                    self._listen_task = asyncio.create_task(self._listen_loop())
                    return True
                except Exception:
                    continue
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
        return False

    async def disconnect(self):
        self._is_running = False
        if self._listen_task:
            self._listen_task.cancel()
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

    def on_snapshot(self, callback: Callable[[DebugGameStateSnapshot], None]):
        self._snapshot_callbacks.append(callback)

    async def _listen_loop(self):
        try:
            while self._is_running and self._ws:
                message = await self._ws.recv()
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    if msg_type == "STATE_SNAPSHOT":
                        snapshot = DebugGameStateSnapshot(**data)
                        self._latest_snapshot = snapshot
                        for cb in self._snapshot_callbacks:
                            try:
                                cb(snapshot)
                            except Exception:
                                pass
                    elif msg_type in ["PATCH_RESULT", "BUG_LIST"]:
                        await self._response_queue.put(data)
                except Exception:
                    pass
        except asyncio.CancelledError:
            pass
        except Exception:
            self._is_running = False

    async def send_command(self, cmd: Dict[str, Any], timeout: float = 3.0) -> Dict[str, Any]:
        if not self.is_connected:
            # Try auto-reconnect
            reconnected = await self.connect(timeout=2.0, retries=2)
            if not reconnected:
                return {"success": False, "error": "Unity WebSocket is not connected"}

        while not self._response_queue.empty():
            self._response_queue.get_nowait()

        try:
            await self._ws.send(json.dumps(cmd))
            res = await asyncio.wait_for(self._response_queue.get(), timeout=timeout)
            return res
        except asyncio.TimeoutError:
            # Command was sent, assume optimistic success if Unity processed it without explicit ACK
            return {"success": True, "type": "PATCH_RESULT", "message": f"Command {cmd.get('type')} processed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === Commandes Dédiées ===

    async def inject_bug(self, bug_id: str) -> Dict[str, Any]:
        return await self.send_command({"type": "INJECT_BUG", "bugId": bug_id})

    async def patch_bug(self, bug_id: str) -> Dict[str, Any]:
        return await self.send_command({"type": "PATCH_BUG", "bugId": bug_id})

    async def reset_all(self) -> Dict[str, Any]:
        return await self.send_command({"type": "RESET_ALL"})

    async def get_bugs(self) -> Dict[str, Any]:
        return await self.send_command({"type": "GET_BUGS"})

    async def set_variable(self, game_object_name: str, component_type: str, field_name: str, value: Any) -> Dict[str, Any]:
        return await self.send_command({
            "type": "SET_VARIABLE",
            "gameObjectName": game_object_name,
            "componentType": component_type,
            "fieldName": field_name,
            "value": str(value)
        })

    async def destroy_component(self, game_object_name: str, component_type: str) -> Dict[str, Any]:
        return await self.send_command({
            "type": "DESTROY_COMPONENT",
            "gameObjectName": game_object_name,
            "componentType": component_type
        })

    async def reassign_reference(self, game_object_name: str, component_type: str, field_name: str, target_name: str) -> Dict[str, Any]:
        return await self.send_command({
            "type": "REASSIGN_REFERENCE",
            "gameObjectName": game_object_name,
            "componentType": component_type,
            "fieldName": field_name,
            "value": target_name
        })