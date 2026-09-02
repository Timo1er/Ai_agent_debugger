import os

menu_dir = r"C:\Users\timot\My project (1)\Assets\unity-debugger-bridge\Editor"
os.makedirs(menu_dir, exist_ok=True)

menu_cs = """using UnityEditor;
using UnityEngine;
using AIDebugger.Core;
using AIDebugger.Telemetry;

public static class AIDebuggerMenu
{
    [MenuItem("Tools/AI Debugger/Installer le serveur IA dans la scène", false, 10)]
    public static void SetupAIDebuggerInScene()
    {
        var existing = Object.FindFirstObjectByType<DebuggerServer>();
        if (existing != null)
        {
            Selection.activeGameObject = existing.gameObject;
            EditorUtility.DisplayDialog("AI Debugger", "Le serveur de débogage IA est déjà présent dans la scène sur l'objet '" + existing.gameObject.name + "'.", "OK");
            return;
        }

        var go = new GameObject("[AI-Debugger]");
        Undo.RegisterCreatedObjectUndo(go, "Create AI Debugger");

        go.AddComponent<MainThreadDispatcher>();
        go.AddComponent<DebuggerServer>();
        go.AddComponent<SpatialTracker>();
        go.AddComponent<ProfilerMetricsCollector>();
        go.AddComponent<LogInterceptor>();
        go.AddComponent<RuntimeInspector>();
        go.AddComponent<TimeStepController>();

        Selection.activeGameObject = go;
        Debug.Log("[AI Debugger] Serveur universel de débogage IA installé avec succès sur [AI-Debugger] !");
        EditorUtility.DisplayDialog("AI Debugger", "Le serveur de débogage IA a été installé dans votre scène avec succès !\\n\\nVous pouvez maintenant lancer le jeu en mode Play ([PLAY]).", "Super !");
    }
}
"""

with open(os.path.join(menu_dir, "AIDebuggerMenu.cs"), "w", encoding="utf-8") as f:
    f.write(menu_cs)

server_file = r"C:\Users\timot\My project (1)\Assets\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs"
if os.path.exists(server_file):
    with open(server_file, "r", encoding="utf-8") as f:
        code = f.read()
    if "AddComponentMenu" not in code:
        code = code.replace("public class DebuggerServer : MonoBehaviour", '[AddComponentMenu("AI Debugger/Debugger Server")]\n    public class DebuggerServer : MonoBehaviour')
        with open(server_file, "w", encoding="utf-8") as f:
            f.write(code)

print("Installed AIDebuggerMenu.cs in My project (1) successfully!")