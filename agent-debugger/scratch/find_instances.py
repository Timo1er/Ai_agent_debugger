import os
import re

base_dir = r"C:\Users\timot\My project (1)\Assets\unity-debugger-bridge"
for root, _, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".cs"):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as file:
                lines = file.readlines()
            for idx, line in enumerate(lines):
                if "GetInstanceID" in line:
                    print(f"{f}:{idx+1} -> {line.strip()}")