import os

path = r"C:\Users\timot\Documents\Git dev\2D_game\Assets\Scripts\Core\LevelBootstrapper.cs"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

debugger_inst = """            // 17. S'assurer que le pont [AI-Debugger] est TOUJOURS actif dans la scène !
            if (FindObjectOfType<AIDebugger.Core.DebuggerServer>() == null)
            {
                GameObject debuggerObj = new GameObject("[AI-Debugger]");
                DontDestroyOnLoad(debuggerObj);
                debuggerObj.AddComponent<AIDebugger.Core.MainThreadDispatcher>();
                debuggerObj.AddComponent<AIDebugger.Core.DebuggerServer>();
                debuggerObj.AddComponent<AIDebugger.Core.AIPlayerDriver>();
                debuggerObj.AddComponent<AIDebugger.Core.AIGameMasterController>();
                debuggerObj.AddComponent<AIDebugger.Core.AIGameMenuOperator>();
                debuggerObj.AddComponent<AIDebugger.Core.DeepGameplayLogicAuditor>();
                debuggerObj.AddComponent<AIDebugger.Core.SpatialExplorer>();
                debuggerObj.AddComponent<AIDebugger.Core.PhysicalStressLab>();
                debuggerObj.AddComponent<AIDebugger.Core.CombatActionFuzzer>();
                debuggerObj.AddComponent<AIDebugger.Core.MicroscopicInvariantOracle>();
                debuggerObj.AddComponent<AIDebugger.Telemetry.AIDebuggerOverlay>();
                debuggerObj.AddComponent<AIDebugger.Telemetry.SpatialTracker>();
                debuggerObj.AddComponent<AIDebugger.Telemetry.TrajectoryTunnelingSentinel>();
                debuggerObj.AddComponent<AIDebugger.Telemetry.ProfilerMetricsCollector>();
                debuggerObj.AddComponent<AIDebugger.Telemetry.LogInterceptor>();
                debuggerObj.AddComponent<AIDebugger.Telemetry.TelemetryStreamer>();
                Debug.Log("<color=green><b>[AI DEBUGGER]</b> Pont IA et Serveur WebSocket démarrés avec succès sur ws://127.0.0.1:8080 !</color>");
            }
"""

if "AIDebugger.Core.DebuggerServer" not in code:
    code = code.replace("Debug.Log(\"<color=green><b>[BuggyPlatformer]</b>", debugger_inst + "\n            Debug.Log(\"<color=green><b>[BuggyPlatformer]</b>")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Added [AI-Debugger] auto-instantiation to LevelBootstrapper.cs")