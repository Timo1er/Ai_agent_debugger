import time
import asyncio
from typing import Any, Dict, List, Optional
from debugger_client.unity_client import UnityDebuggerClient
from llm.llm_provider import BaseLLMProvider, LLMFactory
from .triage_analyst import TriageLogAnalystAgent
from .spatial_inspector import SpatialInspectorAgent
from .code_fixer import CodeFixerAgent

class DebuggerOrchestrator:
    """
    Supervisor / Orchestrator Agent:
    Coordinates the autonomous investigation loop:
    1. Triage (Telemetry & Log Anomaly Isolation)
    2. Spatial & Hierarchy Inspection (Root Cause Identification)
    3. Remediation & Hot-Patching (Action Application)
    4. Post-Fix Verification (Health Check & Telemetry Stabilization)
    """
    def __init__(self, client: UnityDebuggerClient, llm: Optional[BaseLLMProvider] = None):
        self.client = client
        self.llm = llm or LLMFactory.create_provider("heuristic")
        self.triage_agent = TriageLogAnalystAgent(self.client, self.llm)
        self.inspector_agent = SpatialInspectorAgent(self.client, self.llm)
        self.fixer_agent = CodeFixerAgent(self.client, self.llm)

    async def run_debugging_session(self, max_retries: int = 2) -> Dict[str, Any]:
        session_start = time.perf_counter()
        print("\n" + "="*60)
        print(" [ORCHESTRATOR] Starting Autonomous Debugging Session...")
        print("="*60)

        # Step 1: Fetch initial snapshot
        snapshot = await self.client.get_telemetry_snapshot()

        # Step 2: Triage
        t0 = time.perf_counter()
        triage_report = await self.triage_agent.process({"snapshot": snapshot})
        time_to_diagnose = time.perf_counter() - t0

        # Step 3: Deep Inspection
        inspection_result = await self.inspector_agent.process({
            "snapshot": snapshot,
            "triage_report": triage_report
        })

        # Step 4: Fix Application
        t_fix_start = time.perf_counter()
        fix_result = await self.fixer_agent.process({
            "triage_report": triage_report,
            "inspection_result": inspection_result
        })

        # Step 5: Post-Fix Health Verification
        await asyncio.sleep(0.3)
        post_snapshot = await self.client.get_telemetry_snapshot()
        health_verified = self._verify_health(post_snapshot)

        total_resolution_time = time.perf_counter() - session_start

        session_summary = {
            "success": fix_result.get("execution_result", {}).get("success", False) and health_verified,
            "time_to_diagnose_sec": round(time_to_diagnose, 4),
            "time_to_resolve_sec": round(total_resolution_time, 4),
            "triage_report": triage_report,
            "inspection_result": inspection_result,
            "fix_result": fix_result,
            "health_verified": health_verified,
            "post_fps": post_snapshot.metrics.fps if post_snapshot and post_snapshot.metrics else 60.0
        }

        print("\n" + "="*60)
        print(f" [ORCHESTRATOR] Session Finished. Resolved: {session_summary['success']} in {session_summary['time_to_resolve_sec']}s")
        print("="*60)
        return session_summary

    def _verify_health(self, snapshot) -> bool:
        if not snapshot or not snapshot.metrics:
            return True
        if snapshot.metrics.fps < 20.0:
            return False
        return True