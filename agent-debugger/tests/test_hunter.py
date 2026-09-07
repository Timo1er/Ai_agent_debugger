import os
import pytest
import asyncio
from agents.multi_agent_supervisor import MultiAgentSupervisor
from llm.llm_provider import LLMFactory

class DummyDeepClient:
    async def get_spatial_3d(self): return []
    async def get_telemetry_snapshot(self): return None
    async def load_game_level(self, lvl): return True
    async def click_button(self, name): return True
    async def set_god_mode(self, val): return True
    async def start_player_exploration(self, duration): return True
    async def teleport(self, x, y, z): return True
    async def get_tunneling_events(self): return []
    async def call(self, method, args=None): return {}

    async def audit_gameplay_bugs(self):
        return [
            {
                "title": "Détection du sol erronée : GroundCheck au centre",
                "domain": "Physics & Movement",
                "severity": "CRITICAL",
                "description": "groundCheckPoint est nul.",
                "fix": "groundCheckPoint sous les pieds."
            }
        ]

@pytest.mark.asyncio
async def test_multi_agent_supervisor_multilevel():
    client = DummyDeepClient()
    llm = LLMFactory.create_provider("heuristic")
    supervisor = MultiAgentSupervisor(client, llm, duration_seconds=0.3)
    
    report = await supervisor.execute_multi_level_campaign(num_levels=3, duration_per_level=0.1)
    assert report["quality_score"] >= 0
    assert len(report["level_reports"]) == 3
    assert os.path.exists("reports/global_qa_report.md")