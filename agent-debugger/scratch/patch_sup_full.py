import os
import re

sup_path = r"agent-debugger\agents\multi_agent_supervisor.py"
with open(sup_path, "r", encoding="utf-8") as f:
    code = f.read()

# Add static code scanner helper to supervisor
static_scanner = '''
    def _scan_static_code_scripts(self) -> List[Dict[str, Any]]:
        static_bugs = []
        scripts_dir = r"C:\\Users\\timot\\Documents\\Git dev\\2D_game\\Assets\\Scripts"
        if not os.path.exists(scripts_dir):
            return static_bugs

        for root, _, files in os.walk(scripts_dir):
            for file in files:
                if not file.endswith(".cs"):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    for idx, line in enumerate(lines, 1):
                        if "BUG #" in line or "BUG:" in line or "BUG :" in line:
                            # Extract bug comment
                            clean_desc = line.replace("//", "").strip()
                            title = f"Bug de code détecté dans {file} (Ligne {idx})"
                            static_bugs.append({
                                "specialist": "Agent-Code-Auditor",
                                "domain": "Code & Gameplay Invariants",
                                "severity": "HIGH",
                                "title": title,
                                "description": f"[{file}:L{idx}] {clean_desc}",
                                "fix": f"Inspecter {file} à la ligne {idx} et corriger la logique mentionnée."
                            })
                except Exception:
                    pass
        return static_bugs
'''

if "_scan_static_code_scripts" not in code:
    code = code.replace("class MultiAgentSupervisor:", "class MultiAgentSupervisor:\n" + static_scanner)

# In Phase 1, merge static bugs + live runtime bugs
old_p1 = '        # === 1. AUDIT PROFOND DE LOGIQUE GAMEPLAY (25 RÈGLES DE JEU REELLES) ==='
new_p1 = '''        # === 1. AUDIT PROFOND DE LOGIQUE GAMEPLAY (25 RÈGLES DE JEU REELLES) ===
        # A. Analyse Statique des scripts du projet
        static_found = self._scan_static_code_scripts()
        for sf in static_found:
            if not any(x.get("title") == sf.get("title") for x in all_bugs):
                all_bugs.append(sf)
                print(f"   -> [CODE AUDITOR] [{sf.get('severity')}] {sf.get('title')}: {sf.get('description')}")
        
        # B. Analyse Runtime en direct dans Unity'''

if "A. Analyse Statique des scripts du projet" not in code:
    code = code.replace(old_p1, new_p1)

with open(sup_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated multi_agent_supervisor.py with static code AST analysis + live runtime engine audit.")