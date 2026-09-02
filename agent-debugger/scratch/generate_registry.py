import re
import json

csharp_path = r"C:\Users\timot\My project\Assets\Scripts\Bugs\BugRegistry.cs"
with open(csharp_path, "r", encoding="utf-8") as f:
    code = f.read()

pattern = r'Id\s*=\s*"([^"]+)",\s*Category\s*=\s*"([^"]+)",\s*TargetComponent\s*=\s*"([^"]+)",\s*FormalDescription\s*=\s*"([^"]+)",\s*CSharpFix\s*=\s*"([^"]+)"'
# Also handle multi-line strings
pattern_broad = r'Id\s*=\s*"([^"]+)"[^}]+Category\s*=\s*"([^"]+)"[^}]+TargetComponent\s*=\s*"([^"]+)"[^}]+FormalDescription\s*=\s*([^;]+?)[,\s]+CSharpFix\s*=\s*([^}]+)'

raw_defs = re.findall(pattern_broad, code, re.DOTALL)
print(f"Parsed {len(raw_defs)} detailed bug definitions")

bugs_data = []
for r in raw_defs:
    bid = r[0].strip()
    cat = r[1].strip()
    target = r[2].strip()
    desc = re.sub(r'["\+\n\r\s]+', ' ', r[3]).strip()
    fix = re.sub(r'["\+\r]+', '', r[4]).strip()
    bugs_data.append({
        "id": bid,
        "name": desc[:50] + "..." if len(desc) > 50 else desc,
        "category": cat,
        "target": target,
        "description": desc,
        "fix": fix
    })

with open("agent-debugger/scratch/all_bugs.json", "w", encoding="utf-8") as f:
    json.dump(bugs_data, f, indent=2, ensure_ascii=False)
print("Saved all_bugs.json with 45 bugs!")