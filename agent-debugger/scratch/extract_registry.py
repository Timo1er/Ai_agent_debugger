import re
import json

csharp_path = r"C:\Users\timot\My project\Assets\Scripts\Bugs\BugRegistry.cs"
with open(csharp_path, "r", encoding="utf-8") as f:
    code = f.read()

pattern = r'Id\s*=\s*"([^"]+)",\s*Category\s*=\s*"([^"]+)",\s*TargetComponent\s*=\s*"([^"]+)"'
matches = re.findall(pattern, code)

print(f"Total bugs found: {len(matches)}")
all_bugs = []
for m in matches:
    all_bugs.append({
        "id": m[0],
        "category": m[1],
        "target": m[2]
    })

print(json.dumps(all_bugs, indent=2))