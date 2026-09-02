import os
import re

def update_files_in_dir(target_dir):
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(".cs") or file == "UnityCompat.cs":
                continue
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()

            modified = False

            # Replace FindAnyObjectByType
            if "Object.FindAnyObjectByType" in code:
                code = code.replace("Object.FindAnyObjectByType", "UnityCompat.FindAny")
                modified = True
            elif "FindAnyObjectByType" in code:
                code = re.sub(r'FindAnyObjectByType<([^>]+)>\(\)', r'UnityCompat.FindAny<\1>()', code)
                modified = True

            # Replace FindObjectsByType
            if "FindObjectsByType" in code:
                code = re.sub(r'UnityEngine\.Object\.FindObjectsByType<([^>]+)>\(FindObjectsInactive\.Include\)', r'UnityCompat.FindAll<\1>(true)', code)
                code = re.sub(r'UnityEngine\.Object\.FindObjectsByType<([^>]+)>\(FindObjectsInactive\.Exclude\)', r'UnityCompat.FindAll<\1>(false)', code)
                code = re.sub(r'Object\.FindObjectsByType<([^>]+)>\(FindObjectsInactive\.Include\)', r'UnityCompat.FindAll<\1>(true)', code)
                code = re.sub(r'Object\.FindObjectsByType<([^>]+)>\(FindObjectsInactive\.Exclude\)', r'UnityCompat.FindAll<\1>(false)', code)
                modified = True

            # Replace linearVelocity
            if "linearVelocity" in code:
                code = re.sub(r'([a-zA-Z0-9_]+)\.linearVelocity\s*=\s*([^;]+);', r'\1.SetLinearVelocity(\2);', code)
                code = re.sub(r'([a-zA-Z0-9_]+)\.linearVelocity', r'\1.GetLinearVelocity()', code)
                modified = True

            if modified:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code)
                print(f"Patched {file}")

update_files_in_dir(r"C:\Users\timot\My project (1)\Assets\AIDebuggerBridge")
update_files_in_dir(r"c:\Users\timot\Documents\Git dev\AI-agent-debugger\unity-debugger-bridge")