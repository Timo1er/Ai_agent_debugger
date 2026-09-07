using UnityEditor;
using UnityEngine;
using AIDebugger.Core;

namespace AIDebugger.Editor
{
    /// <summary>
    /// Lanceur Automatique du Serveur IA en Arrière-Plan de l'Éditeur Unity.
    /// Garantit que le serveur WebSocket ws://127.0.0.1:8080 est TOUJOURS ouvert et accessible,
    /// que Unity soit en mode Édition ou en mode Jeu (Play Mode).
    /// </summary>
    [InitializeOnLoad]
    public static class AIDebuggerEditorLauncher
    {
        static AIDebuggerEditorLauncher()
        {
            EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
            EnsureServerRunning();
        }

        private static void OnPlayModeStateChanged(PlayModeStateChange state)
        {
            if (state == PlayModeStateChange.EnteredPlayMode || state == PlayModeStateChange.EnteredEditMode)
            {
                EnsureServerRunning();
            }
        }

        public static void EnsureServerRunning()
        {
            var server = UnityCompat.FindAny<DebuggerServer>();
            if (server == null)
            {
                var go = new GameObject("[AI-Debugger]");
                go.hideFlags = HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
                go.AddComponent<MainThreadDispatcher>();
                server = go.AddComponent<DebuggerServer>();
                go.AddComponent<AIPlayerDriver>();
                go.AddComponent<AIGameMasterController>();
                go.AddComponent<AIGameMenuOperator>();
                go.AddComponent<DeepGameplayLogicAuditor>();
                go.AddComponent<SpatialExplorer>();
                go.AddComponent<PhysicalStressLab>();
                go.AddComponent<CombatActionFuzzer>();
                go.AddComponent<MicroscopicInvariantOracle>();
                go.AddComponent<Telemetry.AIDebuggerOverlay>();
                go.AddComponent<Telemetry.SpatialTracker>();
                go.AddComponent<Telemetry.TrajectoryTunnelingSentinel>();
                go.AddComponent<Telemetry.ProfilerMetricsCollector>();
                go.AddComponent<Telemetry.LogInterceptor>();
                go.AddComponent<Telemetry.TelemetryStreamer>();

                if (Application.isPlaying)
                {
                    Object.DontDestroyOnLoad(go);
                }
            }

            if (server != null && !server.IsRunning)
            {
                server.StartServer(8080);
            }
        }
    }
}