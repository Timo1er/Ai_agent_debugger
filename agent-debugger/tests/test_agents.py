import pytest
import asyncio
from debugger_client.unity_client import UnityDebuggerClient
from benchmark.mock_unity_server import MockUnityServer
from agents.triage_analyst import TriageLogAnalystAgent
from agents.spatial_inspector import SpatialInspectorAgent
from agents.code_fixer import CodeFixerAgent
from agents.orchestrator import DebuggerOrchestrator
from llm.llm_provider import HeuristicExpertProvider

@pytest.mark.asyncio
async def test_multi_agent_debugging_flow():
    server = MockUnityServer(port=8091)
    await server.start()

    client = UnityDebuggerClient(port=8091)
    assert await client.connect()

    # Inject NRE chaos
    await client.inject_chaos("null_reference_cascade")

    llm = HeuristicExpertProvider()
    orchestrator = DebuggerOrchestrator(client, llm)
    session = await orchestrator.run_debugging_session()

    assert session["success"] is True
    assert session["triage_report"]["anomaly_type"] == "NULL_REFERENCE_CASCADE"
    assert session["inspection_result"]["target_object"] == "Player3D"
    assert "SET" in session["fix_result"]["runtime_command"]

    await client.disconnect()
    await server.stop()