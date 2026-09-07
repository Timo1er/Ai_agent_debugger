import os

def patch_server(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    autostart_code = """        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void AutoStartOnPlayMode()
        {
            if (UnityCompat.FindAny<DebuggerServer>() == null)
            {
                var go = new GameObject("[AI-Debugger]");
                DontDestroyOnLoad(go);
                go.AddComponent<MainThreadDispatcher>();
                go.AddComponent<DebuggerServer>();
                go.AddComponent<AIPlayerDriver>();
                go.AddComponent<AIGameMasterController>();
                go.AddComponent<AIGameMenuOperator>();
                go.AddComponent<DeepGameplayLogicAuditor>();
                go.AddComponent<SpatialExplorer>();
                go.AddComponent<PhysicalStressLab>();
                go.AddComponent<CombatActionFuzzer>();
                go.AddComponent<MicroscopicInvariantOracle>();
                go.AddComponent<AIDebuggerOverlay>();
                go.AddComponent<SpatialTracker>();
                go.AddComponent<TrajectoryTunnelingSentinel>();
                go.AddComponent<ProfilerMetricsCollector>();
                go.AddComponent<LogInterceptor>();
                go.AddComponent<TelemetryStreamer>();
                Debug.Log("<color=green><b>[AI DEBUGGER]</b> Serveur et modules IA auto-démarrés sur ws://127.0.0.1:8080 !</color>");
            }
        }
"""
        
    if "AutoStartOnPlayMode" not in code:
        code = code.replace("private void Awake()", autostart_code + "\n        private void Awake()")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Patched DebuggerServer with AutoStartOnPlayMode in {path}")

patch_server(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")
patch_server(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")