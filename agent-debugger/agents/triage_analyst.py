import json
from typing import Any, Dict, List
from .base_agent import BaseAgent
from debugger_client.protocol import TelemetrySnapshot

class TriageLogAnalystAgent(BaseAgent):
    """
    Triage & Log Analyst Agent:
    Monitors telemetry stream, detects FPS drops, memory spikes, exception cascades,
    and classifies anomalies to direct investigation.
    """
    def __init__(self, client, llm):
        super().__init__("TriageAnalyst", "Log & Metric Anomaly Detector", client, llm)

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        snapshot: TelemetrySnapshot = context.get("snapshot")
        if not snapshot:
            snapshot = await self.client.get_telemetry_snapshot()

        anomalies = self._detect_rule_anomalies(snapshot)
        system_prompt = (
            "You are the Triage and Log Analyst Agent for a Unity game engine.\n"
            "Analyze the following metrics, logs, and anomalies. Isolate the faulty system, "
            "determine severity (CRITICAL, HIGH, MEDIUM, LOW), and recommend the next inspection step."
        )

        user_prompt = f"""
Telemetry Data:
- FPS: {snapshot.metrics.fps if snapshot and snapshot.metrics else 'N/A'} (Target: 60)
- Frame Time: {snapshot.metrics.frameTimeMs if snapshot and snapshot.metrics else 'N/A'} ms
- GC Memory: {snapshot.metrics.gcMemoryBytes if snapshot and snapshot.metrics else 0} bytes
- Total Allocated: {snapshot.metrics.totalAllocatedMemoryBytes if snapshot and snapshot.metrics else 0} bytes
- Active Chaos Scenario: {snapshot.activeChaosScenario if snapshot else 'None'}
- Recent Logs / Errors:
{json.dumps([l.model_dump() for l in (snapshot.recentLogs or []) if l.type in ['Error', 'Exception', 'Assert']], indent=2) if snapshot else '[]'}
- Detected Rule Anomalies:
{json.dumps(anomalies, indent=2)}
"""

        response_str = await self.llm.generate_response(system_prompt, user_prompt)
        try:
            analysis = json.loads(response_str)
        except Exception:
            analysis = {"raw_analysis": response_str, "anomalies": anomalies}

        analysis["rule_anomalies"] = anomalies
        self.log(f"Triage complete. Severity: {analysis.get('severity', 'UNKNOWN')}, Anomaly: {analysis.get('anomaly_type', 'NONE')}")
        return analysis

    def _detect_rule_anomalies(self, snapshot: TelemetrySnapshot) -> List[Dict[str, Any]]:
        anomalies = []
        if not snapshot:
            return anomalies

        if snapshot.metrics:
            if snapshot.metrics.fps < 30.0:
                anomalies.append({
                    "type": "SEVERE_FPS_DROP",
                    "value": snapshot.metrics.fps,
                    "threshold": 30.0,
                    "message": f"Frame rate dropped to {snapshot.metrics.fps} FPS."
                })
            if snapshot.metrics.gcMemoryBytes > 50 * 1024 * 1024:
                anomalies.append({
                    "type": "MEMORY_SURGE",
                    "value": snapshot.metrics.gcMemoryBytes,
                    "threshold": 50 * 1024 * 1024,
                    "message": "GC Memory surge exceeding 50 MB threshold."
                })

        if snapshot.recentLogs:
            for log in snapshot.recentLogs:
                if log.type in ["Error", "Exception"]:
                    anomalies.append({
                        "type": "RUNTIME_EXCEPTION",
                        "message": log.message,
                        "stackTrace": log.stackTrace
                    })

        return anomalies