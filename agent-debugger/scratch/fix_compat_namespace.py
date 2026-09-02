import os

def fix_compat_in_dir(target_dir):
    if not os.path.exists(target_dir):
        return
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(".cs"):
                continue
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()

            mod = False
            if "UnityEngine.UnityCompat" in code:
                code = code.replace("UnityEngine.UnityCompat", "AIDebugger.Core.UnityCompat")
                mod = True
            if "Object.UnityCompat" in code:
                code = code.replace("Object.UnityCompat", "AIDebugger.Core.UnityCompat")
                mod = True
            if "UnityCompat." in code and "using AIDebugger.Core;" not in code and file != "UnityCompat.cs":
                code = "using AIDebugger.Core;\n" + code
                mod = True

            if mod:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code)
                print(f"Fixed {file} in {target_dir}")

fix_compat_in_dir(r"C:\Users\timot\Documents\Git dev\2D_game\Assets\unity-debugger-bridge")
fix_compat_in_dir(r"C:\Users\timot\My project (1)\Assets\AIDebuggerBridge")
fix_compat_in_dir(r"c:\Users\timot\Documents\Git dev\AI-agent-debugger\unity-debugger-bridge")