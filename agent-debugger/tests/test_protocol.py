import pytest
from debugger_client.protocol import TelemetrySnapshot, ProfilerMetrics, LogEntryDto, SpatialEntity3D

def test_telemetry_snapshot_serialization():
    metrics = ProfilerMetrics(fps=59.5, frameTimeMs=16.8, gcMemoryBytes=1024000)
    log = LogEntryDto(timestamp="2026-08-31T12:00:00Z", frame=100, type="Error", message="Test error")
    ent = SpatialEntity3D(instanceId=1, name="Player3D", posX=1.0, posY=2.0, posZ=3.0)

    snap = TelemetrySnapshot(
        timestamp="2026-08-31T12:00:00Z",
        frameCount=100,
        timeSinceStartup=10.5,
        timeScale=1.0,
        metrics=metrics,
        recentLogs=[log],
        entities3D=[ent]
    )

    data = snap.model_dump()
    assert data["metrics"]["fps"] == 59.5
    assert len(data["recentLogs"]) == 1
    assert data["entities3D"][0]["name"] == "Player3D"