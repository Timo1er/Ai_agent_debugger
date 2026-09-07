import os

def fix_ondestroy(path):
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    old_ondestroy = """        private void OnDestroy()

        {

            StopServer();

        }"""

    new_ondestroy = """        private void OnDestroy()
        {
            if (_instance == this)
            {
                StopServer();
                _instance = null;
            }
        }"""

    if "if (_instance == this)" not in code:
        code = code.replace("private void OnDestroy()\n\n        {\n\n            StopServer();\n\n        }", new_ondestroy)
        code = code.replace("private void OnDestroy()\r\n\r\n        {\r\n\r\n            StopServer();\r\n\r\n        }", new_ondestroy)
        code = code.replace("private void OnDestroy()\n        {\n            StopServer();\n        }", new_ondestroy)
        code = code.replace("private void OnDestroy()\r\n        {\r\n            StopServer();\r\n        }", new_ondestroy)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Fixed OnDestroy in {path}")

fix_ondestroy(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")
fix_ondestroy(r"C:\Users\timot\Documents\Git dev\Ai_agent_debugger\unity-debugger-bridge\Runtime\Core\DebuggerServer.cs")