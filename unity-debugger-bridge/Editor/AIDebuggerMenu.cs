using UnityEditor;

using UnityEngine;

using AIDebugger.Core;

using AIDebugger.Telemetry;



public static class AIDebuggerMenu

{

    [MenuItem("Tools/AI Debugger/Installer le serveur IA dans la scène", false, 10)]

    public static void SetupAIDebuggerInScene()

    {

        var existing = UnityCompat.FindAny<DebuggerServer>();

        if (existing != null)

        {

            if (existing.GetComponent<AIDebuggerOverlay>() == null) existing.gameObject.AddComponent<AIDebuggerOverlay>();

            if (existing.GetComponent<AIPlayerDriver>() == null) existing.gameObject.AddComponent<AIPlayerDriver>();

            if (existing.GetComponent<SpatialExplorer>() == null) existing.gameObject.AddComponent<SpatialExplorer>();

            if (existing.GetComponent<PhysicalStressLab>() == null) existing.gameObject.AddComponent<PhysicalStressLab>();

            if (existing.GetComponent<CombatActionFuzzer>() == null) existing.gameObject.AddComponent<CombatActionFuzzer>();

            if (existing.GetComponent<MicroscopicInvariantOracle>() == null) existing.gameObject.AddComponent<MicroscopicInvariantOracle>();



            Selection.activeGameObject = existing.gameObject;

            EditorUtility.DisplayDialog("AI Debugger", "Tous les modules et laboratoires de stress IA sont actifs sur '" + existing.gameObject.name + "'.", "OK");

            return;

        }



        var go = new GameObject("[AI-Debugger]");

        Undo.RegisterCreatedObjectUndo(go, "Create AI Debugger");



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

        go.AddComponent<TimeStepController>();



        Selection.activeGameObject = go;

        Debug.Log("[AI Debugger] Suite complète de Débogage et Laboratoires de Stress IA installés sur [AI-Debugger] !");

        EditorUtility.DisplayDialog("AI Debugger", "La suite complète de test approfondi (Topologie, Stress Physique, Combat, Oracle Microscopique) a été installée avec succès !\n\nVous pouvez lancer le jeu en mode Play (▶️).", "Génial !");

    }

}