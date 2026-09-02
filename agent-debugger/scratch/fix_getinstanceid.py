import os
import glob

dirs_to_fix = [
    r"C:\Users\timot\My project (1)\Assets\unity-debugger-bridge",
    r"c:\Users\timot\Documents\Git dev\AI-agent-debugger\unity-debugger-bridge"
]

for base_dir in dirs_to_fix:
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".cs"):
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8") as file:
                    content = file.read()
                if "GetInstanceID()" in content:
                    content = content.replace(".GetInstanceID()", ".GetHashCode()")
                    with open(fpath, "w", encoding="utf-8") as file:
                        file.write(content)
                    print(f"Fixed GetInstanceID in {f}")

print("Replaced all GetInstanceID with GetHashCode across all bridge scripts!")