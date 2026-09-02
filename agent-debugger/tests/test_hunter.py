import pytest
import asyncio
from agents.multi_agent_supervisor import MultiAgentSupervisor
from llm.llm_provider import LLMFactory

class DummyDeepClient:
    async def get_spatial_3d(self):
        return []

    async def get_telemetry_snapshot(self):
        class Snap:
            class Metrics:
                gcMemoryBytes = 100 * 1024 * 1024
                fps = 60.0
            metrics = Metrics()
            recentLogs = []
            activeCoroutineCount = 5
            warnings = []
        return Snap()

    async def audit_gameplay_bugs(self):
        return [
            {
                "title": "Détection du sol erronée : GroundCheck positionné au centre",
                "domain": "Physics & Movement",
                "severity": "CRITICAL",
                "description": "groundCheckPoint est nul ou pointe au centre.",
                "fix": "groundCheckPoint doit pointer sous les pieds."
            },
            {
                "title": "Incohérence Collider/Trigger sur Hazard",
                "domain": "Physics & Triggers",
                "severity": "CRITICAL",
                "description": "OnCollisionEnter2D avec isTrigger = true.",
                "fix": "Utiliser OnTriggerEnter2D."
            }
        ]

@pytest.mark.asyncio
async def test_multi_agent_supervisor_gameplay():
    client = DummyDeepClient()
    llm = LLMFactory.create_provider("heuristic")
    supervisor = MultiAgentSupervisor(client, llm, duration_seconds=0.1)
    
    report = await supervisor.execute_multi_agent_hunt()
    assert report["bugs_count"] >= 2
    assert any("GroundCheck" in b["title"] for b in report["bugs"])