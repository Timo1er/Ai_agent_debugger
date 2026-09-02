import asyncio
import json
import uuid
from typing import Any, Callable, Dict, List, Optional
import websockets
from .protocol import (
    RpcRequest,
    RpcResponse,
    TelemetrySnapshot,
    GameObjectNode,
    DynamicCodeResult
)

class UnityDebuggerClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self._ws = None
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._notification_handlers: Dict[str, List[Callable[[Any], None]]] = {}
        self._listen_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._latest_snapshot: Optional[TelemetrySnapshot] = None

    @property
    def is_connected(self) -> bool:
        if self._ws is None:
            return False
        if hasattr(self._ws, "open"):
            return self._ws.open
        if hasattr(self._ws, "closed"):
            return not self._ws.closed
        if hasattr(self._ws, "state"):
            return self._ws.state.name == "OPEN"
        return self._is_running

    @property
    def latest_snapshot(self) -> Optional[TelemetrySnapshot]:
        return self._latest_snapshot

    async def connect(self, timeout: float = 3.0, retries: int = 6) -> bool:
        for attempt in range(1, retries + 1):
            try:
                self._ws = await asyncio.wait_for(websockets.connect(self.uri), timeout=timeout)
                self._is_running = True
                self._listen_task = asyncio.create_task(self._listen_loop())
                self.on_notification("telemetry.snapshot", self._on_telemetry_snapshot)
                return True
            except Exception:
                if attempt < retries:
                    print(f"[AI-Debugger] En attente du lancement de Unity Play Mode ([PLAY]) sur {self.uri} (Essai {attempt}/{retries})...")
                    await asyncio.sleep(1.5)
        return False

    async def disconnect(self):
        self._is_running = False
        if self._listen_task:
            self._listen_task.cancel()
        if self._ws:
            await self._ws.close()
            self._ws = None

    def on_notification(self, event_name: str, handler: Callable[[Any], None]):
        if event_name not in self._notification_handlers:
            self._notification_handlers[event_name] = []
        self._notification_handlers[event_name].append(handler)

    def _on_telemetry_snapshot(self, payload: Any):
        try:
            if isinstance(payload, dict):
                self._latest_snapshot = TelemetrySnapshot(**payload)
        except Exception:
            pass

    async def _listen_loop(self):
        try:
            while self._is_running and self._ws:
                message = await self._ws.recv()
                try:
                    data = json.loads(message)
                    if "id" in data and data["id"] in self._pending_requests:
                        future = self._pending_requests.pop(data["id"])
                        if not future.done():
                            if "error" in data and data["error"]:
                                future.set_exception(RuntimeError(data["error"]["message"]))
                            else:
                                future.set_result(data.get("result"))
                    elif "method" in data:
                        method = data["method"]
                        params = data.get("params")
                        if method in self._notification_handlers:
                            for handler in self._notification_handlers[method]:
                                try:
                                    handler(params)
                                except Exception:
                                    pass
                except json.JSONDecodeError:
                    pass
        except asyncio.CancelledError:
            pass
        except Exception:
            self._is_running = False

    async def call(self, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0) -> Any:
        if not self.is_connected:
            raise ConnectionError("Unity client is not connected.")

        req_id = str(uuid.uuid4())
        raw_params = json.dumps(params) if params is not None else None
        req = RpcRequest(id=req_id, method=method, params=raw_params)

        future = asyncio.get_running_loop().create_future()
        self._pending_requests[req_id] = future

        await self._ws.send(req.model_dump_json())
        return await asyncio.wait_for(future, timeout=timeout)

    # === High Level API Methods ===

    async def get_hierarchy(self) -> List[Dict[str, Any]]:
        return await self.call("inspector.getHierarchy")

    async def find_objects(self, name_pattern: str = "", tag: str = "", type_name: str = "") -> List[Dict[str, Any]]:
        return await self.call("inspector.findObjects", {"namePattern": name_pattern, "tag": tag, "typeName": type_name})

    async def set_member(self, instance_id: int, component_type: str, member_name: str, value: Any) -> bool:
        res = await self.call("inspector.setMember", {
            "instanceId": instance_id,
            "componentTypeName": component_type,
            "memberName": member_name,
            "value": str(value)
        })
        return res.get("success", False) if isinstance(res, dict) else False

    async def invoke_method(self, instance_id: int, component_type: str, method_name: str, args: List[Any] = None) -> Any:
        return await self.call("inspector.invokeMethod", {
            "instanceId": instance_id,
            "componentTypeName": component_type,
            "methodName": method_name,
            "args": args or []
        })

    async def set_component_active(self, instance_id: int, component_type: str, active: bool) -> bool:
        res = await self.call("inspector.setComponentActive", {
            "instanceId": instance_id,
            "componentTypeName": component_type,
            "active": active
        })
        return res.get("success", False) if isinstance(res, dict) else False

    async def set_gameobject_active(self, instance_id: int, active: bool) -> bool:
        res = await self.call("inspector.setGameObjectActive", {
            "instanceId": instance_id,
            "active": active
        })
        return res.get("success", False) if isinstance(res, dict) else False

    async def set_time_scale(self, scale: float) -> Dict[str, Any]:
        return await self.call("timestep.setTimeScale", {"scale": scale})

    async def pause(self) -> Dict[str, Any]:
        return await self.call("timestep.pause")

    async def resume(self) -> Dict[str, Any]:
        return await self.call("timestep.resume")

    async def step_frames(self, count: int = 1) -> Dict[str, Any]:
        return await self.call("timestep.stepFrames", {"frames": count})

    async def execute_code(self, code_snippet: str) -> DynamicCodeResult:
        res = await self.call("eval.executeCode", {"code": code_snippet})
        return DynamicCodeResult(**res) if isinstance(res, dict) else DynamicCodeResult(success=False, error="Invalid response")

    async def get_spatial_2d(self) -> List[Dict[str, Any]]:
        return await self.call("spatial.getEntities2D")

    async def get_spatial_3d(self) -> List[Dict[str, Any]]:
        return await self.call("spatial.getEntities3D")

    async def raycast_3d(self, origin: List[float], direction: List[float], max_distance: float = 100.0) -> Dict[str, Any]:
        return await self.call("spatial.raycast3D", {
            "originX": origin[0], "originY": origin[1], "originZ": origin[2],
            "dirX": direction[0], "dirY": direction[1], "dirZ": direction[2],
            "maxDistance": max_distance
        })

    async def inject_chaos(self, scenario_name: str, params: Optional[Dict[str, Any]] = None) -> bool:
        params_json = json.dumps(params) if params else "{}"
        res = await self.call("chaos.inject", {"scenarioName": scenario_name, "parametersJson": params_json})
        return res.get("injected", False) if isinstance(res, dict) else False

    async def reset_chaos(self) -> bool:
        res = await self.call("chaos.reset")
        return res.get("status") == "reset_complete" if isinstance(res, dict) else False

    async def get_chaos_status(self) -> Dict[str, Any]:
        return await self.call("chaos.getStatus")

    async def set_god_mode(self, enabled: bool = True) -> bool:
        res = await self.call("gamemaster.setGodMode", {"args": [str(enabled).lower()]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def set_fly_mode(self, enabled: bool = True, vertical_speed: float = 0.0) -> bool:
        res = await self.call("gamemaster.setFlyMode", {"args": [str(enabled).lower(), str(vertical_speed)]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def teleport(self, x: float, y: float, z: float = 0.0) -> bool:
        res = await self.call("gamemaster.teleport", {"args": [str(x), str(y), str(z)]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def reset_level(self) -> bool:
        res = await self.call("gamemaster.resetLevel")
        return res.get("success", False) if isinstance(res, dict) else False

    async def start_player_exploration(self, duration: float = 30.0) -> bool:
        res = await self.call("player.explore", {"args": [str(duration)]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def drive_player_move(self, move_x: float = 0.0, move_z: float = 1.0, yaw: float = 0.0, sprint: bool = True, jump: bool = False, duration: float = 2.0) -> bool:
        res = await self.call("player.move", {
            "args": [str(move_x), str(move_z), str(yaw), str(sprint).lower(), str(jump).lower(), str(duration)]
        })
        return res.get("success", False) if isinstance(res, dict) else False

    async def drive_player_fuzz(self, duration: float = 3.0) -> bool:
        res = await self.call("player.fuzz", {"args": [str(duration)]})
        return res.get("success", False) if isinstance(res, dict) else False

    async def audit_gameplay_bugs(self) -> List[Dict[str, Any]]:
        res = await self.call("gameplay.auditBugs")
        return res if isinstance(res, list) else []

    async def get_tunneling_events(self) -> List[Dict[str, Any]]:
        res = await self.call("spatial.getTunnelingEvents")
        return res if isinstance(res, list) else []

    async def scan_geometry_360(self) -> Dict[str, Any]:
        res = await self.call("spatial.scanGeometry")
        return res if isinstance(res, dict) else {}

    async def stress_physics_corner(self) -> bool:
        res = await self.call("physics.stressCorner")
        return res.get("success", False) if isinstance(res, dict) else False

    async def stress_physics_velocity(self) -> bool:
        res = await self.call("physics.stressVelocity")
        return res.get("success", False) if isinstance(res, dict) else False

    async def fuzz_combat_weapons(self) -> bool:
        res = await self.call("combat.fuzzWeapons")
        return res.get("success", False) if isinstance(res, dict) else False

    async def run_microscopic_audit(self) -> Dict[str, Any]:
        res = await self.call("oracle.microAudit")
        return res if isinstance(res, dict) else {}

    async def get_telemetry_snapshot(self) -> Optional[TelemetrySnapshot]:
        res = await self.call("telemetry.getSnapshot")
        if res and isinstance(res, dict):
            return TelemetrySnapshot(**res)
        return None