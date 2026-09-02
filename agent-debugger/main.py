import asyncio
import argparse
import sys
import os
from debugger_client.unity_client import UnityDebuggerClient
from debugger_client.debug_game_adapter import DebugGameClient
from agents.multi_agent_supervisor import MultiAgentSupervisor
from agents.orchestrator import DebuggerOrchestrator
from agents.debug_game_orchestrator import DebugGameOrchestrator
from llm.llm_provider import LLMFactory
from benchmark.evaluation_harness import EvaluationBenchmarkHarness
from benchmark.debug_game_benchmark import DebugGameBenchmarkHarness

async def run_live_debugger(host: str, port: int, provider: str, api_key: str, hunt_mode: bool = False, duration: float = 15.0):
    print(f"[AI-Debugger] Connecting to Unity Engine at ws://{host}:{port}...")
    client = UnityDebuggerClient(host=host, port=port)
    connected = await client.connect()
    if not connected:
        print(f"[AI-Debugger] ERROR: Could not connect to Unity on ws://{host}:{port}. Is the Unity scene running in Play Mode?")
        sys.exit(1)

    print("[AI-Debugger] Connected successfully! Initializing Multi-Agent Supervisor...")
    llm = LLMFactory.create_provider(provider, api_key=api_key)

    if hunt_mode:
        supervisor = MultiAgentSupervisor(client, llm, duration_seconds=duration)
        await supervisor.execute_multi_agent_hunt()
        await client.disconnect()
        return

    orchestrator = DebuggerOrchestrator(client, llm)
    print("[AI-Debugger] Multi-Agent Debugger is listening for anomalies & logs (Ctrl+C to quit)...")
    last_print = 0
    try:
        while True:
            await asyncio.sleep(0.5)
            snapshot = await client.get_telemetry_snapshot()
            if snapshot:
                now = asyncio.get_event_loop().time()
                if now - last_print > 3.0:
                    last_print = now
                    fps = snapshot.metrics.fps if snapshot.metrics else 60.0
                    mem = (snapshot.metrics.gcMemoryBytes / (1024*1024)) if snapshot.metrics and hasattr(snapshot.metrics, "gcMemoryBytes") and snapshot.metrics.gcMemoryBytes else 0.0
                    draws = snapshot.metrics.drawCallsCount if snapshot.metrics and hasattr(snapshot.metrics, "drawCallsCount") and snapshot.metrics.drawCallsCount else 0
                    print(f"[Unity Live 3D Telemetry] FPS: {fps:>5.1f} | GC Memory: {mem:>5.1f} MB | Draw Calls: {draws:>3} | TimeScale: {snapshot.timeScale}")

                has_error = snapshot.recentLogs and any(l.type in ["Error", "Exception"] for l in snapshot.recentLogs)
                fps_low = snapshot.metrics and snapshot.metrics.fps < 25.0
                if has_error or fps_low:
                    print("\n[AI-Debugger] Detected live anomaly! Deploying specialized multi-agent squad...")
                    supervisor = MultiAgentSupervisor(client, llm, duration_seconds=duration)
                    await supervisor.execute_multi_agent_hunt()
    except KeyboardInterrupt:
        print("\n[AI-Debugger] Disconnecting...")
    finally:
        await client.disconnect()

async def run_debug_game_live(host: str, port: int, provider: str, api_key: str, hunt_mode: bool = False, duration: float = 15.0):
    print(f"[AI-Debugger] Connexion au serveur de télémétrie de Unity sur ws://{host}:{port}/ ...")
    client = DebugGameClient(host=host, port=port)
    connected = await client.connect(timeout=5.0, retries=4)
    if not connected:
        print(f"\n[AI-Debugger] ERREUR : Impossible d'établir la liaison WebSocket avec ws://{host}:{port}/")
        print(" -> Vérifiez que le projet est en mode PLAY dans Unity Editor.")
        print(" -> Ou pour lancer le benchmark autonome sans Unity : python main.py --debug-game --mock")
        sys.exit(1)

    print(f"[AI-Debugger] Connecté avec succès à Unity (ws://{host}:{port}/) !")
    llm = LLMFactory.create_provider(provider, api_key=api_key)

    if hunt_mode:
        supervisor = MultiAgentSupervisor(client, llm, duration_seconds=duration)
        await supervisor.execute_multi_agent_hunt()
        await client.disconnect()
        return

    orchestrator = DebugGameOrchestrator(client, llm)
    await orchestrator.initialize()

    print("[AI-Debugger] Superviseur IA actif : Détection & Résolution automatique des bugs en temps réel (Ctrl+C pour quitter)...")
    
    last_print = 0
    try:
        while True:
            await asyncio.sleep(0.1)
            snap = client.latest_snapshot
            if snap:
                await orchestrator.handle_snapshot(snap)
                
                now = asyncio.get_event_loop().time()
                if now - last_print > 3.0:
                    last_print = now
                    bugs_str = ", ".join(snap.activeBugIds) if snap.activeBugIds else "Aucun (Scène Stable)"
                    print(f"[Télémétrie 10Hz] FPS: {snap.fps:>5.1f} | Mémoire: {snap.memoryMB:>5.1f} MB | Coroutines: {snap.activeCoroutineCount:>3} | Bugs Actifs: {bugs_str}")
    except KeyboardInterrupt:
        print("\n[AI-Debugger] Déconnexion...")
    finally:
        await client.disconnect()

def main():
    parser = argparse.ArgumentParser(description="AI Agent Universal Debugger & Multi-Agent Squad for Unity 2D & 3D")
    parser.add_argument("--host", default="127.0.0.1", help="Unity Debugger host IP")
    parser.add_argument("--port", type=int, default=8080, help="Unity Debugger port (default 8080, Debug-game uses 8765)")
    parser.add_argument("--provider", default="heuristic", choices=["heuristic", "gemini", "openai"], help="LLM Provider")
    parser.add_argument("--api-key", default=None, help="LLM API Key")
    parser.add_argument("--benchmark", action="store_true", help="Run automated benchmark evaluation")
    parser.add_argument("--hunt", action="store_true", help="Deploy Multi-Agent Squad to hunt bugs autonomously")
    parser.add_argument("--duration", type=float, default=15.0, help="Duration in seconds of the autonomous hunt campaign (default 15.0s)")
    parser.add_argument("--debug-game", action="store_true", help="Target 'Debug-game-for-AI' environment (port 8765)")
    parser.add_argument("--mock", action="store_true", help="Use embedded Mock server for offline benchmark testing")

    args = parser.parse_args()

    if args.debug_game:
        port = args.port if args.port != 8080 else 8765
        if args.benchmark or args.mock:
            harness = DebugGameBenchmarkHarness(host=args.host, port=port, use_mock=args.mock)
            asyncio.run(harness.run_benchmark())
        else:
            asyncio.run(run_debug_game_live(args.host, port, args.provider, args.api_key, hunt_mode=args.hunt, duration=args.duration))
    elif args.benchmark:
        harness = EvaluationBenchmarkHarness(port=8099)
        asyncio.run(harness.run_benchmark())
    else:
        asyncio.run(run_live_debugger(args.host, args.port, args.provider, args.api_key, hunt_mode=args.hunt, duration=args.duration))

if __name__ == "__main__":
    main()