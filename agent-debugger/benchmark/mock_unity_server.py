import asyncio
import json
import time
from typing import Dict, Any, List, Optional
import websockets

class MockUnityServer:
    """
    High-fidelity Mock Unity Debugger Server for standalone benchmarking & offline testing.
    Emulates JSON-RPC 2.0 API, TimeStep controller, Chaos Engine scenarios, and Reflection inspection.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self._server = None
        self._clients = set()
        self.time_scale = 1.0
        self.is_paused = False
        self.active_chaos_scenario: Optional[str] = None
        self.game_state = self._init_default_state()
        self._stream_task = None

    def _init_default_state(self) -> Dict[str, Any]:
        return {
            "fps": 60.0,
            "frameTimeMs": 16.6,
            "gcMemoryBytes": 15 * 1024 * 1024,
            "totalAllocatedBytes": 45 * 1024 * 1024,
            "logs": [],
            "entities2D": [
                {"instanceId": 101, "name": "Player2D", "posX": 0.0, "posY": 1.0, "velocityX": 0.0, "velocityY": 0.0, "hasCollider2D": True}
            ],
            "entities3D": [
                {"instanceId": 201, "name": "Player3D", "posX": 0.0, "posY": 1.0, "posZ": 0.0, "velocityX": 0.0, "velocityY": 0.0, "velocityZ": 0.0, "hasCollider": True, "collisionDetectionMode": "Continuous"}
            ]
        }

    async def start(self):
        self._server = await websockets.serve(self._handle_client, self.host, self.port)
        self._stream_task = asyncio.create_task(self._stream_telemetry_loop())

    async def stop(self):
        if self._stream_task:
            self._stream_task.cancel()
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _handle_client(self, websocket):
        self._clients.add(websocket)
        try:
            async for message in websocket:
                response = await self._process_message(message)
                if response:
                    await websocket.send(json.dumps(response))
        except Exception:
            pass
        finally:
            self._clients.discard(websocket)

    async def _stream_telemetry_loop(self):
        try:
            while True:
                await asyncio.sleep(0.2)
                if self._clients:
                    snapshot = self._create_snapshot()
                    msg = json.dumps({
                        "jsonrpc": "2.0",
                        "method": "telemetry.snapshot",
                        "params": snapshot
                    })
                    active_clients = [c for c in list(self._clients) if getattr(c, "open", True)]
                    if active_clients:
                        await asyncio.gather(*[c.send(msg) for c in active_clients], return_exceptions=True)
        except asyncio.CancelledError:
            pass

    def _create_snapshot(self) -> Dict[str, Any]:
        return {
            "timestamp": "2026-08-31T12:00:00Z",
            "frameCount": 1000,
            "timeSinceStartup": 50.0,
            "timeScale": self.time_scale,
            "metrics": {
                "fps": self.game_state["fps"],
                "frameTimeMs": self.game_state["frameTimeMs"],
                "gcMemoryBytes": self.game_state["gcMemoryBytes"],
                "totalAllocatedMemoryBytes": self.game_state["totalAllocatedBytes"],
                "totalReservedMemoryBytes": 128 * 1024 * 1024,
                "activeGameObjectsCount": 15,
                "totalComponentsCount": 42,
                "drawCallsCount": 8
            },
            "recentLogs": self.game_state["logs"],
            "entities2D": self.game_state["entities2D"],
            "entities3D": self.game_state["entities3D"],
            "recentCollisions": [],
            "activeChaosScenario": self.active_chaos_scenario
        }

    async def _process_message(self, message: str) -> Optional[Dict[str, Any]]:
        try:
            req = json.loads(message)
            req_id = req.get("id", "null")
            method = req.get("method")
            params = json.loads(req.get("params", "{}")) if req.get("params") else {}

            result = await self._execute_method(method, params)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": "null", "error": {"code": -32603, "message": str(e)}}

    async def _execute_method(self, method: str, params: Dict[str, Any]) -> Any:
        if method == "inspector.getHierarchy":
            return [
                {
                    "instanceId": 1,
                    "name": "SandboxManager",
                    "tag": "Untagged",
                    "components": [{"typeName": "SandboxManager", "enabled": True}]
                },
                {
                    "instanceId": 201,
                    "name": "Player3D",
                    "tag": "Player",
                    "components": [
                        {"typeName": "Transform", "enabled": True},
                        {"typeName": "Rigidbody", "enabled": True},
                        {"typeName": "Player3DController", "enabled": True, "fields": {"moveSpeed": 8.0, "isStunned": False, "targetTransform": None}}
                    ]
                }
            ]

        elif method == "inspector.findObjects":
            return [{"instanceId": 201, "name": "Player3D", "tag": "Player"}]

        elif method == "inspector.setMember":
            return {"success": True}

        elif method == "timestep.setTimeScale":
            self.time_scale = params.get("scale", 1.0)
            self.is_paused = self.time_scale == 0
            return {"timeScale": self.time_scale, "isPaused": self.is_paused}

        elif method == "timestep.pause":
            self.time_scale = 0.0
            self.is_paused = True
            return {"paused": True, "timeScale": 0.0}

        elif method == "timestep.resume":
            self.time_scale = 1.0
            self.is_paused = False
            return {"paused": False, "timeScale": 1.0}

        elif method == "timestep.stepFrames":
            return {"stepped": params.get("frames", 1)}

        elif method == "eval.executeCode":
            code = params.get("code", "")
            if self.active_chaos_scenario:
                self._revert_chaos()
            return {
                "success": True,
                "returnValue": f"Executed: {code}",
                "logs": "[DEBUG] Code evaluated successfully.",
                "executionTimeMs": 1.5
            }

        elif method == "spatial.getEntities2D":
            return self.game_state["entities2D"]

        elif method == "spatial.getEntities3D":
            return self.game_state["entities3D"]

        elif method == "chaos.inject":
            scenario = params.get("scenarioName", "")
            self._inject_chaos(scenario)
            return {"scenario": scenario, "injected": True}

        elif method == "chaos.reset":
            self._revert_chaos()
            return {"status": "reset_complete"}

        elif method == "chaos.getStatus":
            return {"activeScenario": self.active_chaos_scenario}

        elif method == "telemetry.getSnapshot":
            return self._create_snapshot()

        return {}

    def _inject_chaos(self, scenario_name: str):
        self.active_chaos_scenario = scenario_name
        if scenario_name == "null_reference_cascade":
            self.game_state["logs"] = [{
                "timestamp": "2026-08-31T12:00:01Z",
                "frame": 1005,
                "type": "Exception",
                "message": "[PlayerController] NullReferenceException in Update() loop: targetTransform is NULL",
                "stackTrace": "at PlayerController.UpdateMovement()"
            }]
        elif scenario_name == "physics_tunneling":
            self.game_state["entities3D"] = [{
                "instanceId": 999, "name": "ChaosProjectile",
                "posX": 0.0, "posY": 2.0, "posZ": 50.0,
                "velocityX": 0.0, "velocityY": 0.0, "velocityZ": 500.0,
                "hasCollider": True, "collisionDetectionMode": "Discrete"
            }]
        elif scenario_name == "memory_leak":
            self.game_state["gcMemoryBytes"] = 120 * 1024 * 1024
        elif scenario_name == "infinite_loop_trap":
            self.game_state["fps"] = 4.2
            self.game_state["frameTimeMs"] = 238.0
        elif scenario_name == "logic_race_condition":
            self.game_state["logs"] = [{
                "timestamp": "2026-08-31T12:00:02Z",
                "frame": 1010,
                "type": "Warning",
                "message": "[StateMachine] Detected invalid race condition state: IsStunned=true, IsAttacking=true, CanMove=false."
            }]

    def _revert_chaos(self):
        self.active_chaos_scenario = None
        self.game_state = self._init_default_state()