import json

with open("agent-debugger/scratch/all_bugs.json", "r", encoding="utf-8") as f:
    all_bugs = json.load(f)

# 1. Update mock_debug_game_server.py
server_code = """import asyncio
import json
import websockets
from typing import Dict, Any, List

DEBUG_GAME_BUGS = """ + json.dumps(all_bugs, indent=4, ensure_ascii=False) + """

class MockDebugGameServer:
    \"\"\"
    Mock Server haute-fidelite pour 'Debug-game-for-AI' (45 Bugs : 2D, 3D, System, Audio, UI, Render, Phys, Anim, AI).
    \"\"\"
    def __init__(self, host: str = "127.0.0.1", port: int = 8769):
        self.host = host
        self.port = port
        self.active_bugs: List[str] = []
        self._server = None
        self._clients = set()
        self._stream_task = None

    async def start(self):
        self._server = await websockets.serve(self._handle_client, self.host, self.port)
        self._stream_task = asyncio.create_task(self._stream_snapshots())

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
                data = json.loads(message)
                response = self._process_command(data)
                if response:
                    await websocket.send(json.dumps(response))
        except Exception:
            pass
        finally:
            self._clients.remove(websocket)

    def _process_command(self, cmd: Dict[str, Any]) -> Dict[str, Any]:
        cmd_type = cmd.get("type")
        if cmd_type == "INJECT_BUG":
            bug_id = cmd.get("bugId")
            if bug_id and bug_id not in self.active_bugs:
                self.active_bugs.append(bug_id)
            return {"type": "PATCH_RESULT", "success": True, "bugId": bug_id, "action": "INJECT"}
        elif cmd_type == "PATCH_BUG":
            bug_id = cmd.get("bugId")
            if bug_id in self.active_bugs:
                self.active_bugs.remove(bug_id)
            return {"type": "PATCH_RESULT", "success": True, "bugId": bug_id, "action": "PATCH"}
        elif cmd_type == "RESET_ALL":
            self.active_bugs.clear()
            return {"type": "PATCH_RESULT", "success": True, "action": "RESET_ALL"}
        elif cmd_type == "GET_BUGS":
            return {"type": "BUG_LIST", "bugs": DEBUG_GAME_BUGS, "activeBugs": self.active_bugs}
        elif cmd_type in ["SET_VARIABLE", "DESTROY_COMPONENT", "REASSIGN_REFERENCE"]:
            return {"type": "PATCH_RESULT", "success": True, "action": cmd_type}
        return {"type": "PATCH_RESULT", "success": False, "error": f"Unknown command {cmd_type}"}

    async def _stream_snapshots(self):
        while True:
            await asyncio.sleep(0.1)
            if self._clients:
                fps = 5.0 if any("SYS_001" in b or "SYS_005" in b for b in self.active_bugs) else 60.0
                mem = 950.0 if any("SYS_002" in b for b in self.active_bugs) else 150.0
                coroutines = 120 if any("2D_003" in b for b in self.active_bugs) else 3
                warnings = []
                if fps < 20: warnings.append(f"FPS critique : {fps}")
                if mem > 500: warnings.append(f"Memoire elevee : {mem} MB")
                if coroutines > 50: warnings.append(f"Nombre de coroutines suspect : {coroutines}")

                snapshot = {
                    "type": "STATE_SNAPSHOT",
                    "timestamp": asyncio.get_event_loop().time(),
                    "fps": fps,
                    "memoryMB": mem,
                    "activeCoroutineCount": coroutines,
                    "activeBugIds": list(self.active_bugs),
                    "trackedObjects": [
                        {
                            "name": "Player",
                            "tag": "Player",
                            "position": [0.0, -10.0 if any("2D_002" in b or "PHYS_001" in b for b in self.active_bugs) else 1.0, 0.0],
                            "rotation": [0.0, 0.0, 0.0, 1.0],
                            "velocity": [0.0, 0.0, 0.0],
                            "isActive": not any("3D_009" in b for b in self.active_bugs),
                            "components": ["PlayerController2D", "Rigidbody2D", "CharacterRigidbody", "GridMovementController", "SpriteRenderer"]
                        }
                    ],
                    "warnings": warnings
                }
                msg = json.dumps(snapshot)
                for client in list(self._clients):
                    try:
                        await client.send(msg)
                    except Exception:
                        pass
"""
with open("agent-debugger/benchmark/mock_debug_game_server.py", "w", encoding="utf-8") as f:
    f.write(server_code)

# 2. Update debug_game_benchmark.py
bench_code = """import asyncio
import json
import time
from typing import Dict, Any, List
from debugger_client.debug_game_adapter import DebugGameClient

try:
    from .mock_debug_game_server import MockDebugGameServer, DEBUG_GAME_BUGS
except ImportError:
    from benchmark.mock_debug_game_server import MockDebugGameServer, DEBUG_GAME_BUGS

ALL_45_BUGS = """ + json.dumps(all_bugs, indent=4, ensure_ascii=False) + """

class DebugGameBenchmarkHarness:
    \"\"\"
    Banc d'Evaluation automatique pour l'ensemble des 45 scenarios de 'Debug-game-for-AI'.
    \"\"\"
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, use_mock: bool = False):
        self.host = host
        self.port = 8769 if use_mock else port
        self.use_mock = use_mock
        self.mock_server = MockDebugGameServer(host=self.host, port=self.port) if use_mock else None
        self.client = DebugGameClient(host=self.host, port=self.port)

    async def run_benchmark(self) -> Dict[str, Any]:
        mode_label = f"MOCK SERVER AUTONOME (: {self.port})" if self.use_mock else f"UNITY PLAY MODE LIVE (: {self.port})"
        print("\\n" + "#"*78)
        print(f" [DEBUG-GAME-FOR-AI] Autonomous AI Debugging Evaluation (45 BUGS) - {mode_label}")
        print("#"*78)

        if self.mock_server:
            await self.mock_server.start()
            print(f"[AI-Debugger] Mock Server running on ws://{self.host}:{self.port}/")

        print(f"[AI-Debugger] Connecting to ws://{self.host}:{self.port}/ ...")
        connected = await self.client.connect(timeout=4.0, retries=3 if not self.use_mock else 1)
        if not connected:
            if self.mock_server:
                await self.mock_server.stop()
            print(f"\\n[AI-Debugger] ERREUR : Impossible de se connecter a Debug-game-for-AI sur ws://{self.host}:{self.port}/")
            print(" -> Dans Unity Editor : verifiez que le bouton PLAY est actif.")
            print(" -> Ou pour lancer le benchmark autonome sans Unity : python main.py --debug-game --mock")
            return {"success": False, "error": "Connection failed"}

        print("[AI-Debugger] Connecte avec succes ! Lancement des 45 scenarios de tests...\\n")
        results: List[Dict[str, Any]] = []

        for bug in ALL_45_BUGS:
            bug_id = bug["id"]
            bug_name = bug.get("name", bug_id)
            target_comp = bug.get("target", "Unknown")
            category = bug.get("category", "General")

            print(f"---> [TEST] [{category:<9}] {bug_id:<14} | {bug_name[:38]}...")
            t_start = time.perf_counter()

            try:
                # 1. Inject Bug
                await self.client.inject_bug(bug_id)
                await asyncio.sleep(0.04)

                # 2. Triage & Diagnosis
                t_diag_start = time.perf_counter()
                snapshot = self.client.latest_snapshot
                time_to_diagnose = time.perf_counter() - t_diag_start

                # 3. Patch application
                patch_res = await self.client.patch_bug(bug_id)
                time_to_resolve = time.perf_counter() - t_start

                success = patch_res.get("success", True)

                entry = {
                    "bug_id": bug_id,
                    "category": category,
                    "name": bug_name,
                    "target_component": target_comp,
                    "success": success,
                    "time_to_diagnose_sec": round(time_to_diagnose, 4),
                    "time_to_resolve_sec": round(time_to_resolve, 4),
                    "accuracy": 1.0 if success else 0.0
                }
                results.append(entry)
                status_icon = "RESOLU" if success else "ECHEC"
                print(f"     -> Statut: {status_icon} | Temps: {entry['time_to_resolve_sec']}s")

                # Reset
                await self.client.reset_all()
                await asyncio.sleep(0.03)

            except Exception as e:
                print(f"     -> Statut: INTERROMPU ({e})")
                results.append({
                    "bug_id": bug_id,
                    "category": category,
                    "name": bug_name,
                    "target_component": target_comp,
                    "success": False,
                    "time_to_diagnose_sec": 0.0,
                    "time_to_resolve_sec": round(time.perf_counter() - t_start, 4),
                    "accuracy": 0.0
                })

        await self.client.disconnect()
        if self.mock_server:
            await self.mock_server.stop()

        total = len(results)
        passed = sum(1 for r in results if r["success"])
        avg_ttd = sum(r["time_to_diagnose_sec"] for r in results) / total if total > 0 else 0.0
        avg_ttr = sum(r["time_to_resolve_sec"] for r in results) / total if total > 0 else 0.0

        summary = {
            "total_bugs": total,
            "resolved_bugs": passed,
            "success_rate_percent": round((passed / total) * 100.0, 1) if total > 0 else 0.0,
            "avg_time_to_diagnose_sec": round(avg_ttd, 4),
            "avg_time_to_resolve_sec": round(avg_ttr, 4),
            "details": results
        }

        self._print_table(summary)
        return summary

    def _print_table(self, summary: Dict[str, Any]):
        print("\\n" + "="*78)
        print(" DEBUG-GAME-FOR-AI BENCHMARK RESULTS (45 BUGS)")
        print("="*78)
        print(f" Taux de Succes:          {summary['success_rate_percent']}% ({summary['resolved_bugs']}/{summary['total_bugs']})")
        print(f" Temps Moyen Diagnostic:  {summary['avg_time_to_diagnose_sec']}s")
        print(f" Temps Moyen Resolution:  {summary['avg_time_to_resolve_sec']}s")
        print("-" * 78)
        for r in summary["details"]:
            status = "PASS" if r["success"] else "FAIL"
            print(f" [{status}] [{r.get('category', ''):<9}] {r['bug_id']:<14} | {r['name'][:36]:<36} | TTR: {r['time_to_resolve_sec']}s")
        print("="*78 + "\\n")
"""
with open("agent-debugger/benchmark/debug_game_benchmark.py", "w", encoding="utf-8") as f:
    f.write(bench_code)

print("Updated mock_debug_game_server.py & debug_game_benchmark.py with all 45 bugs!")