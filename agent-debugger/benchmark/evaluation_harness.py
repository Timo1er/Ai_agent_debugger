import asyncio
import json
import time
from typing import Dict, Any, List
from debugger_client.unity_client import UnityDebuggerClient
from agents.orchestrator import DebuggerOrchestrator
from llm.llm_provider import LLMFactory

try:
    from .mock_unity_server import MockUnityServer
except ImportError:
    from benchmark.mock_unity_server import MockUnityServer

CHAOS_SCENARIOS = [
    {
        "id": "null_reference_cascade",
        "name": "NullReference Crash Cascade",
        "expected_anomaly": "NULL_REFERENCE_CASCADE",
        "expected_target": "Player3D"
    },
    {
        "id": "physics_tunneling",
        "name": "Physics Tunneling & CCD Failure",
        "expected_anomaly": "PHYSICS_TUNNELING",
        "expected_target": "ChaosProjectile"
    },
    {
        "id": "memory_leak",
        "name": "Catastrophic Memory Surge",
        "expected_anomaly": "MEMORY_LEAK",
        "expected_target": "[AIDebugger_ChaosEngine]"
    },
    {
        "id": "infinite_loop_trap",
        "name": "Infinite Loop Frame Drop (<5 FPS)",
        "expected_anomaly": "FRAME_FREEZE_INFINITE_LOOP",
        "expected_target": "[AIDebugger_ChaosEngine]"
    },
    {
        "id": "logic_race_condition",
        "name": "Logic State Machine Stalemate",
        "expected_anomaly": "STATE_MACHINE_DESYNC",
        "expected_target": "Player3D"
    }
]

class EvaluationBenchmarkHarness:
    def __init__(self, port: int = 8089):
        self.port = port
        self.mock_server = MockUnityServer(port=port)
        self.client = UnityDebuggerClient(port=port)
        self.llm = LLMFactory.create_provider("heuristic")
        self.orchestrator = DebuggerOrchestrator(self.client, self.llm)

    async def run_benchmark(self) -> Dict[str, Any]:
        print("\n" + "#"*70)
        print(" [BENCHMARK HARNESS] Starting Autonomous AI Debugger Evaluation...")
        print("#"*70)

        await self.mock_server.start()
        connected = await self.client.connect()
        if not connected:
            raise RuntimeError("Failed to connect benchmark client to server.")

        results: List[Dict[str, Any]] = []

        for scenario in CHAOS_SCENARIOS:
            print(f"\n---> Running Benchmark Scenario: {scenario['name']} ({scenario['id']})")

            # 1. Inject Chaos
            await self.client.inject_chaos(scenario["id"])
            await asyncio.sleep(0.1)

            # 2. Run Autonomous Debugger Orchestration
            session = await self.orchestrator.run_debugging_session()

            # 3. Compute Metrics
            triage_anomaly = session.get("triage_report", {}).get("anomaly_type", "")
            target_obj = session.get("inspection_result", {}).get("target_object", "")

            anomaly_correct = triage_anomaly == scenario["expected_anomaly"]
            target_correct = target_obj == scenario["expected_target"]
            accuracy_score = (1.0 if anomaly_correct else 0.0) * 0.5 + (1.0 if target_correct else 0.0) * 0.5

            result_entry = {
                "scenario_id": scenario["id"],
                "scenario_name": scenario["name"],
                "success": session["success"],
                "time_to_diagnose_sec": session["time_to_diagnose_sec"],
                "time_to_resolve_sec": session["time_to_resolve_sec"],
                "accuracy_score": accuracy_score,
                "post_fps": session["post_fps"],
                "fix_strategy": session.get("fix_result", {}).get("fix_strategy", "N/A")
            }
            results.append(result_entry)

            # Reset between tests
            await self.client.reset_chaos()
            await asyncio.sleep(0.1)

        await self.client.disconnect()
        await self.mock_server.stop()

        # Generate Benchmark Summary
        total_tests = len(results)
        resolved_count = sum(1 for r in results if r["success"])
        avg_ttd = sum(r["time_to_diagnose_sec"] for r in results) / total_tests
        avg_ttr = sum(r["time_to_resolve_sec"] for r in results) / total_tests
        avg_accuracy = (sum(r["accuracy_score"] for r in results) / total_tests) * 100.0

        summary = {
            "total_scenarios": total_tests,
            "resolved_scenarios": resolved_count,
            "success_rate_percent": round((resolved_count / total_tests) * 100.0, 1),
            "average_time_to_diagnose_sec": round(avg_ttd, 4),
            "average_time_to_resolve_sec": round(avg_ttr, 4),
            "average_diagnostic_accuracy_percent": round(avg_accuracy, 1),
            "scenarios_detail": results
        }

        self._print_summary_table(summary)
        return summary

    def _print_summary_table(self, summary: Dict[str, Any]):
        print("\n" + "="*70)
        print(" BENCHMARK EVALUATION RESULTS SUMMARY")
        print("="*70)
        print(f" Success Rate:            {summary['success_rate_percent']}% ({summary['resolved_scenarios']}/{summary['total_scenarios']})")
        print(f" Avg Diagnostic Accuracy: {summary['average_diagnostic_accuracy_percent']}%")
        print(f" Avg Time to Diagnose:     {summary['average_time_to_diagnose_sec']}s")
        print(f" Avg Time to Resolve:      {summary['average_time_to_resolve_sec']}s")
        print("-" * 70)
        for r in summary["scenarios_detail"]:
            status_icon = "PASS" if r["success"] else "FAIL"
            print(f" [{status_icon}] {r['scenario_name']:<35} | TTD: {r['time_to_diagnose_sec']}s | TTR: {r['time_to_resolve_sec']}s | Acc: {int(r['accuracy_score']*100)}%")
        print("="*70 + "\n")

async def main():
    harness = EvaluationBenchmarkHarness(port=8099)
    await harness.run_benchmark()

if __name__ == "__main__":
    asyncio.run(main())