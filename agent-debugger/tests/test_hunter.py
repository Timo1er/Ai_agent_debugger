import pytest
import asyncio
from agents.multi_agent_supervisor import MultiAgentSupervisor
from llm.llm_provider import LLMFactory

class DummyDeepClient:
    async def get_spatial_3d(self):
        return [{"name": "Player", "posY": -35.0, "velocityX": 0, "velocityY": -50, "velocityZ": 0}]

    async def get_telemetry_snapshot(self):
        class Snap:
            class Metrics:
                gcMemoryBytes = 600 * 1024 * 1024
                fps = 18.0
            metrics = Metrics()
            recentLogs = [{"type": "Exception", "message": "NullReferenceException in EnemyAI.Update()"}]
            activeCoroutineCount = 65
            warnings = ["ANOMALY_FOG: Fog too dense"]
        return Snap()

    async def scan_geometry_360(self):
        return {"openBounds": 24}

    async def run_microscopic_audit(self):
        return {
            "pinkShadersFound": 2,
            "nanCoordinatesFound": 1,
            "audioListenerMuted": True,
            "playerIgnoresEnemies": True
        }

@pytest.mark.asyncio
async def test_multi_agent_supervisor():
    client = DummyDeepClient()
    llm = LLMFactory.create_provider("heuristic")
    supervisor = MultiAgentSupervisor(client, llm, duration_seconds=0.1)
    
    report = await supervisor.execute_multi_agent_hunt()
    assert report["bugs_count"] >= 5